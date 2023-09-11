import math, os, shutil, sys

def getNumBitsToReserve(num):
    """
    Gets the size of the given number in terms of bits.
    :param num: The number in decimal format, whose bit size will be calculated and returned.
    :return: The number of bits needed to store 'num'.
    """
    return math.ceil(math.log2(num + 1)) if num > 0 else 1


def removePreviouslyExtractedData(extracted_data_path):
    """
    Removes all data located inside of the folder of the specified path.
    :param extracted_data_path: The path to the folder containing all contents that need to be deleted.
    """
    try:
        for item in os.listdir(extracted_data_path):
            item_path = os.path.join(extracted_data_path, item)
            
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

def removePotentialHiddenFiles(folder_path):
    """
    Checks to see if there are any hidden files, whose names start with '.', and if so, removes them.
    :param folder_path: The path to the folder that will be checked for any potential hidden files.
    """
    try:
        folder_contents = os.listdir(folder_path)
        
        for item in folder_contents:
            item_path = os.path.join(folder_path, item)
            
            # Check if the item is a hidden file (starts with a dot)
            if item.startswith('.') and not item.lower().endswith('.png'):
                os.remove(item_path)
    except Exception as e:
        print(f"An error occurred: {str(e)}")