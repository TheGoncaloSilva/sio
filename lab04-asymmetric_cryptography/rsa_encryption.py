# Lecture: http://sweet.ua.pt/jpbarraca/course/sio-2223/lab-crypto-asymmetric/
# Good source: https://gist.github.com/gabrielfalcao/de82a468e62e73805c59af620904c124
import sys
import generate_rsa as KEYS
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def read_public_key(fileName):
    with open(fileName, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
        )
        return public_key

def read_file(fileName):
    with open(fileName, "rb") as f:
        return f.read()

def write_to_file(fileName, data):
    with open(fileName, "wb") as f:
        f.write(data)

def main(argv):
    readFileName = "text.txt"
    encryptedFileName = "encrypted"
    privateFeyFile = "keys/private_key.pem"
    publicKeyFile = "keys/public_key.pem"
    keySize = 1024
    if len(argv) >= 2:
        readFileName = argv[1]
    if len(argv) >= 3:
        encryptedFileName = argv[2]
    if len(argv) >= 4:
        try:
            keySize = int(argv[3])
        except:
            raise ValueError("Wrong key format")
            exit(1)

    #KEYS.main([None, keySize, privateFeyFile, publicKeyFile])
    # Read the public key from the file (in PEM format)
    publicKey = read_public_key(publicKeyFile)
    
    # Read the data of file in bytes format
    fileData = read_file(readFileName)

    encrypted = publicKey.encrypt(
        fileData,
        padding.PKCS1v15()
    )
    write_to_file(encryptedFileName, encrypted)

main(sys.argv)