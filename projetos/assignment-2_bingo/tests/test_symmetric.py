import pytest
import sys

from common.symmetric import *

def test_generate_key():
    keySize = 16
    key = generate_key(keySize)
    assert len(key) == keySize

def test_encrypt():
    key = generate_key(16)
    values = "random values  1"
    ciphertext = encrypt_values(values, key)
    assert isinstance(ciphertext, bytes)

def test_decrypt():
    key = generate_key(16)
    values = "random values  1"
    ciphertext = encrypt_values(values, key)
    plaintext = decrypt_values(ciphertext, key)
    assert values == plaintext

def test_key_to_and_from_string():
    key = generate_key(16)
    assert isinstance(bytes_to_string(key), str)
    key_to_string = bytes_to_string(key)
    key2 = bytes_from_string(key_to_string)
    assert key == key2

    


