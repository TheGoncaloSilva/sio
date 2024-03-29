import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from rsa_decryption import read_file, write_to_file


def utf8(s: bytes):
    return str(s, 'utf-8')


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
)
public_key = private_key.public_key()


private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

with open('keys/private_key.pem', 'wb') as f:
    f.write(private_pem)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
with open('keys/public_key.pem', 'wb') as f:
    f.write(public_pem)


with open("keys/private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

with open("keys/public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

data = read_file("text.txt")

print(f'plaintext: \033[1;33m{utf8(data)}\033[0m')
encrypted = base64.b64encode(public_key.encrypt(
    data,
    padding.PKCS1v15()
))
print(f'encrypted: \033[1;32m{utf8(encrypted)}\033[0m')
write_to_file("encrypted", encrypted)

encrypted_data = read_file("encrypted")

decrypted = private_key.decrypt(
    base64.b64decode(encrypted_data),
    padding.PKCS1v15()
)
print(f'decrypted: \033[1;31m{utf8(decrypted)}\033[0m')

write_to_file("decrypted", decrypted)