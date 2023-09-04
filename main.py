from Image_Manipulation import ImageDataExtraction, ImageDataHiding
import os


if __name__ == "__main__":
    # Stored directory containing your local computer's path up to this project directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
   
    # If the path leads to a folder, add an extra '/' at the end of the path if you only want to hide 
    # the contents of all data located inside of the folder. 
    # Otherwise, the program will hide the folder itself as well, containing all the contents.
    path_to_data_you_want_hidden = ""

    path_to_input_photos = script_directory + '/Input_Photos'
    path_to_processed_photos = script_directory + '/Processed_Photos'
    path_to_paste_data = script_directory + '/Extracted_Data'

    print("Enter 1 to hide data in an image set.")
    print("Enter 2 to extract data from an image set")
    num = input()
    print("***")

    if num == '1':
        ImageDataHiding.hideDataInImages(path_to_data_you_want_hidden, path_to_input_photos, path_to_processed_photos)
    elif num == '2':
        ImageDataExtraction.extractDataFromImages(path_to_processed_photos, path_to_paste_data)
    else:
        print("Invalid response.")



