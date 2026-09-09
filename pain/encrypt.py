import json
import os
import hashlib
from cryptography.fernet import Fernet

# ============================================================
# Utility Functions
# ============================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ============================================================
# Encryption Setup
# ============================================================

def load_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as f:
            f.write(key)
    else:
        with open("secret.key", "rb") as f:
            key = f.read()
    return Fernet(key)

fernet = load_key()

def encrypt_array(arr):
    data = ",".join(map(str, arr)).encode()
    return fernet.encrypt(data).decode()

def decrypt_array(token):
    data = fernet.decrypt(token.encode()).decode()
    return list(map(int, data.split(",")))

# ============================================================
# Account System
# ============================================================

def create_account(users):
    username = input("Choose a username: ")
    if username in users:
        print("Username already exists.")
        return

    password = input("Choose a password: ")
    hashed = hash_password(password)

    users[username] = {
        "password": hashed,
        "data": None
    }

    save_users(users)
    print("Account created successfully.")

def login(users):
    username = input("Username: ")
    if username not in users:
        print("User not found.")
        return None

    password = input("Password: ")
    if hash_password(password) == users[username]["password"]:
        print("Login successful.")
        return username
    else:
        print("Incorrect password.")
        return None

def reset_password(users):
    username = input("Enter your username: ")
    if username not in users:
        print("User not found.")
        return

    old = input("Enter old password: ")
    if hash_password(old) != users[username]["password"]:
        print("Incorrect old password.")
        return

    new = input("Enter new password: ")
    users[username]["password"] = hash_password(new)
    save_users(users)
    print("Password updated.")

# ============================================================
# Array Operations
# ============================================================

def input_array():
    arr = []
    while True:
        val = input("Enter number (or 'done'): ")
        if val.lower() == "done":
            break
        try:
            arr.append(int(val))
        except:
            print("Invalid input.")
    return arr

def save_user_array(users, username, arr):
    encrypted = encrypt_array(arr)
    users[username]["data"] = encrypted
    save_users(users)
    print("Array saved (encrypted).")

def load_user_array(users, username):
    encrypted = users[username]["data"]
    if encrypted is None:
        print("No saved data.")
        return []
    return decrypt_array(encrypted)

# ============================================================
# Menu System
# ============================================================

def main_menu():
    users = load_users()
    logged_in = None

    while True:
        print("\n===== MAIN MENU =====")
        print("1. Login")
        print("2. Create Account")
        print("3. Reset Password")
        print("4. Exit")

        choice = input("Choose: ")

        if choice == "1":
            logged_in = login(users)
            if logged_in:
                user_menu(users, logged_in)

        elif choice == "2":
            create_account(users)

        elif choice == "3":
            reset_password(users)

        elif choice == "4":
            print("Goodbye.")
            break

        else:
            print("Invalid choice.")

def user_menu(users, username):
    while True:
        print(f"\n===== USER MENU ({username}) =====")
        print("1. Enter new array")
        print("2. Load saved array")
        print("3. Save current array")
        print("4. Logout")

        choice = input("Choose: ")

        if choice == "1":
            arr = input_array()
            print("Your array:", arr)

        elif choice == "2":
            arr = load_user_array(users, username)
            print("Loaded array:", arr)

        elif choice == "3":
            arr = input_array()
            save_user_array(users, username, arr)

        elif choice == "4":
            print("Logged out.")
            break

        else:
            print("Invalid choice.")

# ============================================================
# Run Program
# ============================================================

main_menu()
