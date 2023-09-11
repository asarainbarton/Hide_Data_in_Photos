import os
import sys


def writeByteDataToFile(destination_file, byte_data):
    """
    Data in byte format is written to the appropriate file, named destination_file.
    :param destination_file: The name of the destination file we want to create and write our data to.
    :param byte_data: The data in byte format that will get written to the destination file.
    """
    with open(destination_file, 'wb') as destination:
        destination.write(byte_data)


def createDirectoryFromByteData(folder_path, byte_data_list):
    """
    Creates a directory inside 'folder_path', containing all the data in 'byte_data_list'.
    :param folder_path: The location where all the data will be recreated.
    :param byte_data_list: The dictionary representation of an entire directory's contents.
    """
    # Specified path must lead to a folder
    if not os.path.isdir(folder_path):
        print("Error - Specified directory for adding data leads to a file - not a folder.")
        sys.exit(1)
    
    for key, value in byte_data_list.items():
        # Current dictionary value is recognized as a folder
        if type(value) == dict:
            sub_dir_path = os.path.join(folder_path, key.decode('utf-8'))

            # Otherwise, a FileExistsError exception would be thrown
            if sub_dir_path != folder_path + "/":
                os.mkdir(sub_dir_path)
            
            createDirectoryFromByteData(sub_dir_path, value)
            continue
        
        file_path = os.path.join(folder_path, key.decode('utf-8'))
        
        # Creates a file at the specified path if one does not exist and then writes the byte data to it
        writeByteDataToFile(file_path, value)