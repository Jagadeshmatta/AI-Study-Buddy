import json
import os

USER_FILE = "users.json"


# ---------- LOAD USERS ----------
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)


# ---------- SAVE USERS ----------
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)


# ---------- REGISTER (EMAIL LOGIN) ----------
def register(email, password):
    users = load_users()

    if email in users:
        return False, "User already exists"

    users[email] = {
        "password": password
    }

    save_users(users)
    return True, "Account created successfully"


# ---------- LOGIN ----------
def login(email, password):
    users = load_users()

    if email in users and users[email]["password"] == password:
        return True

    return False