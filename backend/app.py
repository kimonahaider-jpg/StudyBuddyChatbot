from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_PATH = "../database/study_buddy.db"

def get_db():
    return sqlite3.connect(DB_PATH)

@app.route("/")
def home():
    return jsonify({"status": "running"})

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "❗ Empty message."})

    conn = get_db()
    cur = conn.cursor()

    # Save user message
    cur.execute(
        "INSERT INTO chat_history (role, message) VALUES (?, ?)",
        ("user", user_message)
    )

    # Simple rule-based reply
    if "hello" in user_message.lower():
        reply = "👋 Hey! I remember our chats now."
    else:
        reply = "🧠 Message saved. AI brain coming soon."

    # Save bot reply
    cur.execute(
        "INSERT INTO chat_history (role, message) VALUES (?, ?)",
        ("assistant", reply)
    )

    conn.commit()
    conn.close()

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
