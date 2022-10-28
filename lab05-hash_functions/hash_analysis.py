import sys, random

def read_messages(fileName):
    with open(fileName, "rb") as f:
        return f.read()

def create_variations(message, variations):
    data = []
    message = bin(int(message.hex(), base=16)).lstrip('0b')
    for i in range(variations):
        index = random.randrange(len(message))
        new_msg = list(message)
        new_msg[index] = str(int(not new_msg[index]))
        string = ''.join(new_msg)
        data.append(int(string, base=16))
    
    return data


def main(argv):
    fileReadName = "messages.txt"
    nVariations = 10
    if len(argv) > 1:
        fileReadName = argv[1]

    if len(argv) > 2:
        nVariations = int(argv[2])
    
    message = read_messages(fileReadName)

    variations = create_variations(message, nVariations)
    print(variations)

main(sys.argv)