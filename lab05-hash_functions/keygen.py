from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sys, os

kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(), 
        length = 32, 
        salt = os.urandom(16), 
        iterations = 100000
    )

password = input("Password: ")
data = kdf.derive(password)

iv = data[:16]
key = data[16:]
