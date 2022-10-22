# Good source: https://gist.github.com/gabrielfalcao/de82a468e62e73805c59af620904c124
import sys
import generate_rsa as KEYS
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

def read_public_key(fileName):
    with open(fileName, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
        )

def read_file(fileName):
    with open(fileName, "rb") as f:
        return f.read()

def write_to_file(fileName, data):
    with open(fileName, "rb") as f:
        f.write(data)

def main(argv):
    readFileName = "text.txt"
    encryptedFileName = "encrypted.txt"
    privateFeyFile = "keys/private_key.pem"
    publicKeyFile = "keys/public_key.pem"
    keySize = 2048

    KEYS.main([None, keySize, privateFeyFile, publicKeyFile])
    # Read the public key from the file (in PEM format)
    publicKey = read_public_key(publicKeyFile)
    # Read the data of file in bytes format
    fileData = read_file(readFileName)

    encrypted = publicKey.encrypt(
        fileData,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
)
    


main(sys.argv)