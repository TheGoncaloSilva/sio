# Lecture: http://sweet.ua.pt/jpbarraca/course/sio-2223/lab-crypto-hash-functions/
import sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def main(argv):
    fileWData = "data.txt"
    if len(argv) > 1 and argv[1] not in ["MD5", "SHA256", "SHA384", "SHA512", "Blake2"]:
        raise ValueError("Please choose a available hash function")
        exit(1)

    # Read file
    data = b''
    with open(fileWData, "rb") as f:
        data = f.read()

    # Create the hash
    if argv[1] == "MD5":
        digest = hashes.Hash(hashes.MD5())
    elif argv[1] == "SHA256":
        digest = hashes.Hash(hashes.SHA256())
    elif argv[1] == "SHA384":
        digest = hashes.Hash(hashes.SHA384())
    elif argv[1] == "SHA512":
        digest = hashes.Hash(hashes.SHA512())
    elif argv[1] == "Blake2":
        digest = hashes.Hash(hashes.BLAKE2b(64))
    else:
        raise ValueError("Error occurred in hash usage")
        exit(1)

    # Hash the value
    digest.update(data)
    hashValue = digest.finalize()

    # Print the hash in hexadecimal
    print(hashValue.hex())
    return hashValue.hex




main(sys.argv)