# src/auth.py

import json
import os

USER_FILE = os.path.join(os.path.dirname(__file__), "user.json")

# Load users
def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_FILE, "r") as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Register new user
def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

# Authenticate login
def authenticate_user(username, password):
    users = load_users()
    return users.get(username) == password
