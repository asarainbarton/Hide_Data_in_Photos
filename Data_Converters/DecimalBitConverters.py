import sys


def convertDecimalToBits(num, requiredLength):
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
    bit_length = len(bits)
    num = 0

    for i in range(bit_length):
        if bits[i] == 1:
            num += 2 ** (bit_length - i - 1)

    return num