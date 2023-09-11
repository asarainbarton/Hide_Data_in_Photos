import sys


def convertDecimalToBits(num, requiredLength):
    """
    Converts any natural number (including zero) to its binary representation.
    :param num: The nonnegative integer to be converted into binary.
    :param requiredLength: The required length, in bits, that the binary value should be.
    :return: The number in binary format, represented as a bytearray.
    """
    binary_string = bin(num)[2:]
    bits = bytearray(map(int, binary_string))

    # num cannot be negative
    if num < 0:
        print("Error - Only zero or positive integers are allowed to be converted to binary string format")
        sys.exit(1)

    # There is a maximum amount of space that a number in binary format can occupy and can't exceed
    if len(bits) > requiredLength:
        print("Error - Number " + str(num) + " is too large to be converted into a binary string of size " + str(requiredLength))
        sys.exit(1)
    
    temp = bytearray()
    for i in range(requiredLength - len(bits)):
        temp.append(0)
    
    return temp + bits


def convertBitsToDecimal(bits):
    """
    Converts a nonnegative number represented in binary to its appropriate decimal value.
    :param bits: The binary data, represented as a bytearray.
    :return: The binary value in decimal (integer) format.
    """
    bit_length = len(bits)
    num = 0

    for i in range(bit_length):
        if bits[i] == 1:
            num += 2 ** (bit_length - i - 1)

    return num