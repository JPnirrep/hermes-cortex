import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_secret(secret: str, password: str):
    salt = os.urandom(16)
    key = get_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(secret.encode())
    # On stocke le sel avec le message chiffré
    return base64.b64encode(salt + encrypted).decode()

def decrypt_secret(token: str, password: str):
    try:
        data = base64.b64decode(token)
        salt, encrypted = data[:16], data[16:]
        key = get_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted).decode()
    except Exception:
        return "ERROR: Decryption failed (wrong password?)"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: vault.py [encrypt/decrypt] [text] [password]")
        sys.exit(1)
    
    action = sys.argv[1]
    text = sys.argv[2]
    password = sys.argv[3] if len(sys.argv) > 3 else "AG-MASTER-VAULT-2026"

    if action == "encrypt":
        print(encrypt_secret(text, password))
    elif action == "decrypt":
        print(decrypt_secret(text, password))
