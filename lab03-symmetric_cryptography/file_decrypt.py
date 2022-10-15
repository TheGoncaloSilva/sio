import os, sys, base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# argv usage: encripted_file key iv decryption_algorythm
def main(argv):

    fileR = "encrypted.txt"
    fileKeyW = "key.txt"
    encAlgo = "AES"
    fileW = "decrypted.txt"

    if len(argv) >= 1:
        fileR = argv[0]
    
    if len(argv) >= 2:
        fileKeyW = argv[1]

    if len(argv) >= 3:
        if encAlgo == "AES" or encAlgo == "ChaCha20":
            encAlgo = argv[2]
        else:
            raise ValueError("Encryption algorythm only AES or ChaCha20, switching to AES")

    with open(fileKeyW, "rb") as f:
        key = f.read(32)
        iv = f.read(16)
    
    if encAlgo == "AES":
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    else:
        cipher = Cipher(algorithms.ChaCha20(key, nonce=iv), mode=None)

    rData = []
    with open(fileR, "rb") as f:
        rData.append(f.read(16))

    with open(fileW, "w") as f:
        padded_data = bytes(''.join(rData), 'utf-8')
        unpadder = padding.PKCS7(16).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        decryptor = cipher.decryptor()
        f.write(str(decryptor.update(data) + decryptor.finalize()))


if __name__ == "__main__":
	main(sys.argv)