"""
    `symmetric` module, focused on symmetric encryption handling
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import base64

def generate_key(keySize: int) -> bytes:
    """
        Generate a random key of keySize(keySize must represent the number of bytes, not bits)

        Args:
            - keySize: the key size in bytes

        Returns: 
            A random sequence of bytes (the key)

        Raises:
            - ValueError: If the keySize is not a valid size for a key
    """
    if keySize % 16 != 0:
        raise ValueError("Invalid key size")
    return os.urandom(keySize)


def encrypt_values(values: str, key: bytes) -> bytes:
    """
        Function to encrypt with AES blocks a string with a key and return it as bytes

        Args:
            - values: The values to be encrypted
            - key: The key that is going to encrypt

        Returns:
            The encrypted values and the initialization vector of the mode of the AES algorithm (concatenated)

        Raises:


    """
    iv = os.urandom(len(key))

    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    encryptor = cipher.encryptor()
    cipherText = encryptor.update(values.encode(encoding='utf-8')) + encryptor.finalize()

    return iv + cipherText


def decrypt_values(values: bytes, key: bytes) -> str:
    """
        Function to decrypt an encrypted set of bytes into plaintext

        Args: 
            - values: The values to be decrypted
            - key: The key that is going to decrypt

        Returns:
            The decrypted values

        Raises:
    """
    iv = values[:len(key)]
    values = values[len(key):]

    cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(values) + decryptor.finalize()

    return plaintext.decode(encoding='utf-8')


def bytes_to_string(key: bytes) -> str:
    """
        Function to return a key or encrypted value, in string format 

        Args:
            - key: The key in bytes format to convert

        Returns:
            The key in string format

        Raises:
    """
    return base64.b64encode(key).decode("utf-8")


def bytes_from_string(keyString: str) -> bytes:
    """
        Function to return a key or encrypted value, from its string format

        Args:
            - key: The key in string format to convert

        Returns:
            The key in bytes format

        Raises:
    """
    return base64.b64decode(keyString)


"""
# Test the encrypt_values() function
key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'
iv = b'\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20'
cipher = generate_cipher(key, iv)
print(cipher)

plaintext = "Hello, World!"
ciphertext = encrypt_values(plaintext, cipher, 128)
assert isinstance(ciphertext, bytes)
print(ciphertext)

# Test the decrypt_values() function
decrypted = decrypt_values(ciphertext, cipher, 128)
assert isinstance(decrypted, bytes)
assert decrypted.decode() == plaintext
print(decrypted)

key_string = key_to_string(key)
assert isinstance(key_string, str)
print(key_string)

key_bytes = key_from_string(key_string)
assert isinstance(key_bytes, bytes)
print(key_bytes)
"""