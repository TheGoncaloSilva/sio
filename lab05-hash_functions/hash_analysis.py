import sys, random
import generate_hash as hash_gen

def read_messages(fileName):
    with open(fileName, "rb") as f:
        return f.read()

def gen_stats(hash1, hash2):
    if len(hash1) != len(hash2): raise ValueError("Hashes must be of same length")

    r = b''
    for i in range(len(hash1)):
        v = bin(hash1[i] ^ hash2[i])
        v = v[2:]
        v = '0'*(8-len(v)) + v
        r += v

    n_0 = 0
    n_1 = 0
    for i in r:
        if i == 0 : n_0 += 1
        if i == 1 : n_1 += 1

    return (n0, n1)

def create_variations(message, variations):
    data = []
    message = bin(int(message.hex(), base=16)).lstrip('0b')
    for i in range(variations):
        index = random.randrange(len(message))
        new_list = list(message)
        new_list[index] = str(int(not new_list[index]))
        new_msg = b'';
        row = '0';
        for i, byte in enumerate(new_list):
            if(i % 8 != 0) or i == 0:
                row = bin(int(row, 2) + int(byte, 2))
            else:
                hex_val = int(row, base=16)
                new_msg += bytes.fromhex(hex_val)
                row = '0'

        data.append(new_msg)
    
    return data


def main(argv):
    fileReadName = "messages.txt"
    nVariations = 10
    if len(argv) > 1:
        fileReadName = argv[1]

    if len(argv) > 2:
        nVariations = int(argv[2])
    
    message = read_messages(fileReadName)
    hashed = []
    for msg in message:
        hashed.append()

    variations = create_variations(message, nVariations)
    print(variations)

main(sys.argv)