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

# --- CHAT ROUTE ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    history_context = ""
    
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("SELECT role, message FROM chat_history ORDER BY id DESC LIMIT 3")
            rows = cur.fetchall()
            for role, msg in reversed(rows):
                history_context += f"{role}: {msg}\n"
    except: pass

    # THE SECRET SAUCE: We use "###" to block the AI from rambling
    full_prompt = f"""### SYSTEM:
You are 'Study Buddy', a helpful AI tutor for Kumail.
Answer ONLY as 'Assistant'. 
Give a short 1-sentence answer. 
Stop immediately after your sentence.

### HISTORY:
{history_context}

### NEW MESSAGE:
User: {user_message}
Assistant:"""

    try:
        # We add 'stop' tokens to tell Ollama exactly where to cut off the AI
        response = requests.post("http://localhost:11434/api/generate",
            json={
                "model": "tinydolphin", 
                "prompt": full_prompt, 
                "stream": False,
                "options": {
                    "stop": ["User:", "###", "\n"]
                }
            }, timeout=45)
        reply = response.json().get("response", "").strip()
        # Remove any accidental "User:" parts if the AI still hallucinated
        reply = reply.split("User:")[0].strip()
    except:
        reply = "⚠️ Ollama error."

    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("User", user_message))
            cur.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("Assistant", reply))
            conn.commit()
    except: pass

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