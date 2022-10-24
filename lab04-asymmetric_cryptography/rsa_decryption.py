# Lecture: http://sweet.ua.pt/jpbarraca/course/sio-2223/lab-crypto-asymmetric/
# Good source: https://gist.github.com/gabrielfalcao/de82a468e62e73805c59af620904c124
import sys
import generate_rsa as KEYS
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def read_private_key(fileName):
    with open(fileName, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
        return private_key

def read_file(fileName):
    with open(fileName, "rb") as f:
        return f.read()

def write_to_file(fileName, data):
    with open(fileName, "wb") as f:
        f.write(data)

def main(argv):
    readEncrypted = "encrypted"
    encryptedFileName = "decrypted"
    privateFeyFile = "keys/private_key"
    publicKeyFile = "keys/public_key"
    keySize = 1024

    if len(argv) >= 2:
        readEncrypted = argv[1]
    if len(argv) >= 3:
        encryptedFileName = argv[2]
    if len(argv) >= 4:
        try:
            keySize = int(argv[3])
        except:
            raise ValueError("Wrong key format")
            exit(1)
    if len(argv) >= 5:
        privateFeyFile = argv[4]

    private_key = read_private_key(privateFeyFile)
    
    # Read the data of file in bytes format
    fileData = read_file(readEncrypted)

    decrypted = private_key.decrypt(
        fileData,
        padding.PKCS1v15()
    )

    write_to_file(encryptedFileName, decrypted)

main(sys.argv)