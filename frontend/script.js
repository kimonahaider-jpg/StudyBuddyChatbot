const chatBox = document.getElementById('messages');

// 1. CHAT FUNCTION
async function sendChat() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, true); // Add your message to UI
    input.value = '';

    try {
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        addMessage(data.reply, false); // Add Buddy's message to UI
    } catch (error) {
        addMessage("⚠️ Connection failed. Is the Flask server running?", false);
    }
}

// 2. SUMMARIZER FUNCTION
async function summarizeNotes() {
    const note = document.getElementById('noteInput').value;
    const resultDiv = document.getElementById('summaryResult');
    if (!note) return;

    resultDiv.innerText = "⏳ Processing notes...";

    try {
        const response = await fetch('http://localhost:5000/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: note })
        });
        const data = await response.json();
        resultDiv.innerText = data.summary;
    } catch (error) {
        resultDiv.innerText = "⚠️ Error connecting to server.";
    }
}

// 3. PLANNER FUNCTION (To-Do List)
function addTask() {
    const taskInput = document.getElementById('taskInput');
    const taskList = document.getElementById('taskList');
    
    if (taskInput.value.trim() === "") return;

    const li = document.createElement('li');
    li.style.background = "rgba(255,255,255,0.1)";
    li.style.padding = "8px";
    li.style.marginBottom = "5px";
    li.style.borderRadius = "4px";
    li.style.display = "flex";
    li.style.justifyContent = "space-between";
    li.style.alignItems = "center";
    
    li.innerHTML = `
        <span>${taskInput.value}</span>
        <button onclick="this.parentElement.remove()" style="background:none; color:#ff7675; border:none; cursor:pointer; font-weight:bold;">X</button>
    `;
    
    taskList.appendChild(li);
    taskInput.value = "";
}

// 4. UI HELPERS
function addMessage(text, isUser) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
}

function handleKeyPress(e) {
    if (e.key === 'Enter') sendChat();
}