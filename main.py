from Image_Manipulation import ImageDataExtraction, ImageDataHiding
import os


def main():
    # Stored directory containing your local computer's path up to this project directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
       
    """
    ***
    PASTE THE LOCATION OF THE DATA YOU WANT HIDDEN IN THIS VARIABLE!!
    (Otherwise, the given default path will be used)
    ***

    If the path leads to a folder, add an extra '/' at the end of the path if you only 
    want to hide the contents of all data located inside of the folder. Otherwise, the 
    program will hide the folder itself as well, containing all the contents.
    """
    PATH_TO_DATA_YOU_WANT_HIDDEN = ""


    '''
    If a path is not specified by the user, then a default path to a folder will be 
    used which the user can paste any data into that they want hidden.
    '''
    if PATH_TO_DATA_YOU_WANT_HIDDEN == "":
        PATH_TO_DATA_YOU_WANT_HIDDEN = script_directory + '/Data_To_Hide/'

    path_to_input_photos = script_directory + '/Input_Photos'
    path_to_processed_photos = script_directory + '/Processed_Photos'
    path_to_paste_data = script_directory + '/Extracted_Data'

    print("Enter 1 to hide data in an image set.")
    print("Enter 2 to extract data from an image set")
    num = input()
    print("***")

    if num == '1':
        ImageDataHiding.hideDataInImages(PATH_TO_DATA_YOU_WANT_HIDDEN, path_to_input_photos, path_to_processed_photos)
    elif num == '2':
        ImageDataExtraction.extractDataFromImages(path_to_processed_photos, path_to_paste_data)
    else:
        print("Invalid response.")

if __name__ == '__main__':
    main()
