import pickle, sys


def convertBytesToBinaryByteArray(byte_data):
    """
    Converts value of type 'bytes' to its binary representation, where the zeroes and ones are stored in a bytearray.
    :param byte_data: Value of type 'bytes' that will be converted.
    :return: Byte data converted to binary data stored in a bytearray.
    """
    zeroes_ones = bytearray()

    for byte in byte_data:
        binary_representation = bin(byte)[2:].zfill(8)
        zeroes_ones.extend(map(int, binary_representation))

    return zeroes_ones


def convertBinaryByteArrayToBytes(binary_data):
    """
    Converts a bytearray containing zeroes and ones to a variable of type bytes.
    :param binary_data: The binary data that'll be converted to bytes.
    :return: The binary data in byte format.
    """
    byte_string = "".join(map(str, binary_data))
    byte_data = bytearray()

    for i in range(0, len(byte_string), 8):
        byte_value = int(byte_string[i:i+8], 2)
        byte_data.append(byte_value)

    return bytes(byte_data)


def convertByteDataListToFullBinary(byte_data_list):
    """
    Converts a dictionary representation of an entire directory's contents, including all files in all/any subfolders
    and their names into a full string of zeroes and ones.
    :param byte_data_list: The dictionary representation of an entire directory's contents.
    :return: The dictionary representation, represented as binary data stored in a bytearray.
    """
    return convertBytesToBinaryByteArray(pickle.dumps(byte_data_list))


def convertFullBinaryToByteDataList(binary_data):
    """
    Converts binary data stored in a bytearray into a dictionary representation of an entire directory's contents.
    :param binary_data: The binary data that will end up getting converted.
    :return: The dictionary representation of an entire directory's contents, which was created from 'binary_data'.
    """
    byte_data_list = pickle.loads(convertBinaryByteArrayToBytes(binary_data))

    # Data being loaded must load up as a variable of type dictionary, containing all stored data
    if type(byte_data_list) != type(dict()):
        print("Error - Unable to extract data from the given image(s)")
        sys.exit(1)

    return byte_data_list