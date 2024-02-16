import os, sys, base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# argv usage: encripted_file key iv decryption_algorythm
def main(argv):

    fileR = "encrypted.txt"
    fileKeyW = "key.txt"
    #encAlgo = "AES"
    encAlgo = "AES-ECB"
    #encAlgo = "ChaCha20"
    fileW = "decrypted.txt"

    if len(argv) >= 2:
        fileR = argv[1]
    
    if len(argv) >= 3:
        fileKeyW = argv[2]

    if len(argv) >= 4:
        if encAlgo == "AES" or encAlgo == "ChaCha20":
            encAlgo = argv[3]
        else:
            raise ValueError("Encryption algorythm only AES or ChaCha20, switching to AES")

    with open(fileKeyW, "rb") as f:
        key = f.read(32)
        iv = f.read(16)
    
    if encAlgo == "AES":
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    elif encAlgo == "AES-ECB":
        cipher = Cipher(algorithms.AES(key), modes.ECB())
    else:
        cipher = Cipher(algorithms.ChaCha20(key, nonce=iv), mode=None)

    rData = b''
    with open(fileR, "rb") as f:
        rData += f.read()

    with open(fileW, "wb") as f:
        decryptor = cipher.decryptor()
        data = decryptor.update(rData) + decryptor.finalize()
        unpadder = padding.PKCS7(16*8).unpadder()
        data = unpadder.update(data)
        data += unpadder.finalize()
        f.write(data)

        

if __name__ == "__main__":
	main(sys.argv)