import os, sys, base64, secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# argv usage: file_to_read key file_to_write_keys encryption_algorythm
def main(argv):

    #fileR = "file.txt"
    fileR = "eagle.bmp"
    key = os.urandom(32)
    fileKeyW = "key.txt"
    encAlgo = "AES"
    #encAlgo = "AES-ECB"
    #encAlgo = "ChaCha20"
    fileW = "eagle.bmp"

    if len(argv) >= 2:
        fileR = argv[1]

    if len(argv) >= 3:
        key = bytes(argv[2])
    
    if len(argv) >= 4:
        fileKeyW = argv[3]

    if len(argv) >= 5:
        if encAlgo == "AES" or encAlgo == "ChaCha20":
            encAlgo = argv[4]
        else:
            raise ValueError("Encryption algorythm only AES or ChaCha20, switching to AES")

    #iv = os.urandom(16)
    iv = secrets.token_bytes(16)
    
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
        padder = padding.PKCS7(16*8).padder() # 16 bytes by 8 bits
        padded_data = padder.update(rData)
        padded_data += padder.finalize()
        encryptor = cipher.encryptor()
        f.write(encryptor.update(padded_data) + encryptor.finalize())

    with open(fileKeyW, "wb") as f:
        f.write(key)
        f.write(iv)
            

if __name__ == "__main__":
	main(sys.argv)