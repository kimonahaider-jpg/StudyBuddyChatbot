from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION & PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../database/study_buddy.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "../database/schema.sql")

# --- DATABASE SETUP ---
def init_db():
    """Creates the database and table if they don't exist."""
    if not os.path.exists(DB_PATH):
        print("Creating database file...")
    
    with sqlite3.connect(DB_PATH) as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
    print("✅ Database initialized.")

# --- ROUTES ---
@app.route("/")
def home():
    return jsonify({"status": "running", "message": "Study Buddy API is active!"})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "❗ Please type something."})

    # 1. Fetch History from Database (Memory)
    history_context = ""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            # Get last 5 messages
            cur.execute("SELECT role, message FROM chat_history ORDER BY id DESC LIMIT 5")
            rows = cur.fetchall()
            for role, msg in reversed(rows):
                history_context += f"{role}: {msg}\n"
    except Exception as e:
        print(f"Database error: {e}")

    # 2. Prepare the AI Prompt
    full_prompt = f"""
    You are a friendly, helpful offline Study Buddy. 
    Use the following chat history for context.
    
    History:
    {history_context}
    
    Current User Message: {user_message}
    Buddy:"""

    # 3. Call Ollama (Local AI)
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=30 # Wait up to 30 seconds for AI to think
        )
        reply = response.json().get("response", "🤖 Sorry, I couldn't generate a response.")
    except:
        reply = "⚠️ Ollama is not responding. Is the Ollama app open and running?"

    # 4. Save both messages to the Database
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("user", user_message))
            cur.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("assistant", reply))
            conn.commit()
    except Exception as e:
        print(f"Failed to save to DB: {e}")

    return jsonify({"reply": reply})

if __name__ == "__main__":
    init_db() # Ensures the table exists before starting
    app.run(port=5000, debug=True)