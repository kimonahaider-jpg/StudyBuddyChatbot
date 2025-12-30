from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests
from pathlib import Path

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION & PATHS ---
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent 
DB_DIR = ROOT_DIR / "database"
DB_PATH = DB_DIR / "study_buddy.db"
SCHEMA_PATH = DB_DIR / "schema.sql"

def init_db():
    try:
        if not DB_DIR.exists():
            DB_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())
            print(f"✅ Database ready at: {DB_PATH}")
        conn.close()
    except Exception as e:
        print(f"❌ Database Error: {e}")

@app.route("/")
def home():
    return jsonify({"status": "Online"})

# --- CHAT ROUTE (FIXED VERSION) ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    history_context = ""
    
    # 1. GET HISTORY
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("SELECT role, message FROM chat_history ORDER BY id DESC LIMIT 2")
            rows = cur.fetchall()
            for role, msg in reversed(rows):
                history_context += f"{role}: {msg}\n"
    except: pass

    # 2. CREATE PROMPT (Strict "Teacher" Mode)
    # We explicitly tell it NOT to be the user.
    full_prompt = f"""Instructions: You are a helpful AI tutor. 
    Do not simulate the user. Answer the question directly and briefly.

    Previous Chat:
    {history_context}

    User: {user_message}
    Assistant:"""

    reply = ""

    try:
        # 3. CALL OLLAMA
        response = requests.post("http://localhost:11434/api/generate",
            json={
                "model": "tinydolphin", 
                "prompt": full_prompt, 
                "stream": False
            }, timeout=45)
            
        reply = response.json().get("response", "").strip()
        
        # 4. CLEANUP (The "Janitor" work)
        # Remove labels like "Assistant:" or "User:" so the bot sounds natural
        reply = reply.replace("Assistant:", "").replace("User:", "").strip()
        
        # 5. SAFETY NET (If AI returns nothing, force a message)
        if not reply:
            reply = "🤔 I'm not sure how to answer that. Could you rephrase?"

        print(f"🤖 AI SAID: {reply}") 

    except Exception as e:
        print(f"❌ Error: {e}")
        reply = "⚠️ Connection error."

    # 6. SAVE TO DB
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("User", user_message))
            cur.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("Assistant", reply))
            conn.commit()
    except: pass

    # 7. SEND TO FRONTEND (Key must be 'response' to match script.js)
    return jsonify({"reply": reply})

# --- SUMMARIZER ROUTE ---
@app.route("/summarize", methods=["POST"])
def summarize():
    text = request.json.get("text", "").strip()
    if not text: return jsonify({"summary": "Paste notes first!"})
    
    prompt = f"Summarize into 3 bullet points:\n{text}"
    try:
        response = requests.post("http://localhost:11434/api/generate",
            json={"model": "tinydolphin", "prompt": prompt, "stream": False}, timeout=60)
        return jsonify({"summary": response.json().get("response", "")})
    except:
        return jsonify({"summary": "⚠️ Error."})
    
if __name__ == "__main__":
    init_db()
    app.run(port=5000, debug=True)