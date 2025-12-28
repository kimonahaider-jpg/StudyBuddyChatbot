async function send() {
    const input = document.getElementById("input");
    const message = input.value.trim();
    if (!message) return; // Don't send empty messages

    input.value = "";
    addMessage("You", message);

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        if (!response.ok) throw new Error("Server issues");

        const data = await response.json();
        addMessage("Buddy", data.reply);
    } catch (error) {
        addMessage("System", "⚠️ Connection failed. Is the Flask server running?");
    }
}

function addMessage(sender, text) {
    const div = document.createElement("div");
    div.style.marginBottom = "10px"; // Add some spacing
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;
    document.getElementById("messages").appendChild(div);
}