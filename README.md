# 📘 Study Buddy AI

**Course:** Programming for AI (BS AI 3-B)
**Team:** Kumail & Group

## 🚀 Project Overview
Study Buddy is a local, privacy-focused AI assistant designed for students. It runs offline using a Flask backend, SQLite database, and the TinyDolphin LLM via Ollama. It features:
- **AI Chatbot:** Context-aware tutoring with strict persona locking.
- **Summarizer:** Instantly converts notes into bullet points.
- **Local Hosting:** No data leaves the user's machine.

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite3
- **AI Engine:** Ollama (TinyDolphin Model)

## ⚙️ How to Run Locally

1. **Install Dependencies:**
   ```bash
   pip install flask flask-cors requests
2. **Start Ollama:**
   Ensure Ollama is running and the model is pulled:
   ```bash
   ollama pull tinydolphin
3. **Run the Backend:**
   ```bash
   cd backend
   python app.py
4. **Launch the App:**
   Open `frontend/index.html` in your browser.
