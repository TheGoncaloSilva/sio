import sys
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

def check_key_size(key):
    if key == 1024 or key == 2048 or key == 3072 or key == 4096:
        return True
    return False

def save_to_file(file_name, key):
    with open(file_name, 'wb') as f:
        f.write(key)

def main(argv):
    key = 2048
    privateFile = "keys/private_key.pem"
    publicFile = "keys/public_key.pem"

    if len(argv) > 1: 
        if len(argv) >= 2 and check_key_size(argv[1]):
            key = argv[1]
        else:
            raise ValueError("Argument <key> not present or of wrong size")
            exit(1)
        
        if len(argv) >= 3:
            privateFile = argv[2]
        else:
            raise ValueError("Argument <key, private_file> not present or of wrong size")
            exit(2)

        if len(argv) >= 4:
            publicFile = argv[3]
        else:
            raise ValueError("Argument <key, private_file, public_file> not present or of wrong size")
            exit(3)
    
    # Generate keys
    private_key = rsa.generate_private_key(
        public_exponent=65537, 
        key_size=key
    )
    public_key = private_key.public_key()

    # Convert private to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    # Write to file
    save_to_file(privateFile, private_pem)

    # Convert public to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    #Write to file
    save_to_file(publicFile, public_pem)

main(sys.argv)