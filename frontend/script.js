async function send() {
    const input = document.getElementById("input");
    const message = input.value;
    input.value = "";

    addMessage("You", message);

    const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
    });

    const data = await response.json();
    addMessage("Buddy", data.reply);
}

function addMessage(sender, text) {
    const div = document.createElement("div");
    div.textContent = sender + ": " + text;
    document.getElementById("messages").appendChild(div);
}
