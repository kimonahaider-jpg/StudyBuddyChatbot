CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,         -- 'user' or 'assistant'
    message TEXT NOT NULL,      -- The actual chat text
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);