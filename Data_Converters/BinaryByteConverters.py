import pickle, sys


def convertBytesToBinaryByteArray(byte_data):
    zeroes_ones = bytearray()

    for byte in byte_data:
        binary_representation = bin(byte)[2:].zfill(8)
        zeroes_ones.extend(map(int, binary_representation))

    return zeroes_ones


def convertBinaryByteArrayToBytes(binary_data):
    byte_string = "".join(map(str, binary_data))
    byte_data = bytearray()

    for i in range(0, len(byte_string), 8):
        byte_value = int(byte_string[i:i+8], 2)
        byte_data.append(byte_value)

    return bytes(byte_data)


def convertByteDataListToFullBinary(byte_data_list):
    return convertBytesToBinaryByteArray(pickle.dumps(byte_data_list))


def convertFullBinaryToByteDataList(binary_data):
    byte_data_list = pickle.loads(convertBinaryByteArrayToBytes(binary_data))

    # Data being loaded must load up as a variable of type dictionary, containing all stored data
    if type(byte_data_list) != type(dict()):
        print("Error - Unable to extract data from the given image(s)")
        sys.exit(1)

    return byte_data_list