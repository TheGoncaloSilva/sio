import os, sys, base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# argv usage: file_to_read key file_to_write_keys encryption_algorythm
def main(argv):

    fileR = "file.txt"
    key = os.urandom(32)
    fileKeyW = "key.txt"
    encAlgo = "AES"
    #encAlgo = "ChaCha20"
    fileW = "encrypted.txt"

    if len(argv) >= 1:
        fileR = argv[0]

    if len(argv) >= 2:
        key = bytes(argv[1])
    
    if len(argv) >= 3:
        fileKeyW = argv[2]

    if len(argv) >= 4:
        if encAlgo == "AES" or encAlgo == "ChaCha20":
            encAlgo = argv[3]
        else:
            raise ValueError("Encryption algorythm only AES or ChaCha20, switching to AES")

    iv = os.urandom(16)
    
    if encAlgo == "AES":
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    else:
        cipher = Cipher(algorithms.ChaCha20(key, nonce=iv), mode=None)

    rData = []
    with open(fileR, "r") as f:
        rData.append(f.read(16))

    with open(fileW, "wb") as f:
        data = bytes(''.join(rData), 'utf-8')
        padder = padding.PKCS7(16).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        encryptor = cipher.encryptor()
        f.write(encryptor.update(data) + encryptor.finalize())

    with open(fileKeyW, "wb") as f:
        f.write(key)
        f.write(iv)
            

if __name__ == "__main__":
	main(sys.argv)