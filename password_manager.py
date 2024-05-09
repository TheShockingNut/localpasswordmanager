import json
import os
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

def generate_key_from_password(password):
    salt = b'\x00' * 16  # Using a fixed salt for simplicity; consider using a unique salt per user in a real application
    kdf = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    key = base64.urlsafe_b64encode(kdf)
    return key

def hash_master_password(password):
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt + hashed_password

def verify_master_password(stored_password, provided_password):
    salt = stored_password[:16]
    stored_hash = stored_password[16:]
    provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    return stored_hash == provided_hash

def encrypt_text(text, master_key):
    cipher_suite = Fernet(master_key)
    encoded_text = text.encode()
    encrypted_text = cipher_suite.encrypt(encoded_text)
    return encrypted_text.decode()

def decrypt_text(encrypted_text, master_key):
    cipher_suite = Fernet(master_key)
    try:
        decrypted_text = cipher_suite.decrypt(encrypted_text.encode())
        return decrypted_text.decode()
    except InvalidToken:
        raise ValueError("Invalid master password")

def load_passwords(file_path="passwords.json"):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_passwords_to_file(passwords, file_path="passwords.json"):
    with open(file_path, "w") as file:
        json.dump(passwords, file)

def save_master_password(master_password, file_path="master_password.bin"):
    with open(file_path, "wb") as file:
        file.write(master_password)

def load_master_password(file_path="master_password.bin"):
    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            return file.read()
    return None
