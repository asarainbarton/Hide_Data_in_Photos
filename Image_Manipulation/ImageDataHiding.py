from Data_Converters import DirectoryToByteData, BinaryByteConverters, DecimalBitConverters, Miscellaneous_Helpers
from PIL import Image
import pickle, sys, os, math


def hideDataInImages(folder_path, path_to_input_photos, path_to_processed_photos):
    """
    Hides data in a given set of images and saves those modified images to a new folder.
    :param folder_path: The path to the data that we want to extract and hide.
    :param path_to_input_photos: The path to the folder containing the photo(s) that will be used to hide
    the data.
    :param path_to_processed_photos: Folder location where all photos that have been processed will be saved.
    """
    byte_data_list = DirectoryToByteData.getByteData(folder_path)
    bits = BinaryByteConverters.convertByteDataListToFullBinary(byte_data_list)

    # All error checking happens here to determine whether or not photo data can properly be hidden
    checkIfDataCanBeHidden(len(bits), path_to_input_photos)

    printSizeOfDataToBeHidden(len(bits))

    # Any processed photos from a previous session will get removed
    Miscellaneous_Helpers.removePreviouslyExtractedData(path_to_processed_photos)

    # Total number of bits to be hidden in binary (bit) format
    b_total_bits = DecimalBitConverters.convertDecimalToBits(len(bits), Miscellaneous_Helpers.getNumBitsToReserve(len(bits)))

    unused_photos = []

    bit_index = 0
    photo_num = 0
    first_image = True
    for photo in os.listdir(path_to_input_photos):
        photo_path = os.path.join(path_to_input_photos, photo)

        # If true, then all data has been hidden in all previous photo(s) and any remaining photos will not be needed when extracting data.
        if bit_index >= len(bits):
            unused_photos.append(photo)
            continue

        b_photo_num = DecimalBitConverters.convertDecimalToBits(photo_num, Miscellaneous_Helpers.getNumBitsToReserve(photo_num))

        # Hides data in the current photo and updates the next bit index in 'bits' to be stored
        bit_index = hideDataInPhoto(bits, bit_index, photo_path, b_photo_num, b_total_bits, first_image, path_to_processed_photos)
        first_image = False
        photo_num += 1
    
    # This error should never occur but is checked just in case.
    if bit_index < len(bits):
        print("Error - Not all data was able to be hidden in the given photos.")
        print("If this error occurs, something went wrong and the process was unsuccessful")
        sys.exit(1)
    
    print("Your data has successfully been hidden! (100% complete)")
    
    # Any potential remaining photos that didn't need to be used for hiding data are listed here.
    if len(unused_photos) > 0:
        print("\nHere are all the photos that didn't need to (and haven't been) processed...")
        for photo in unused_photos:
            print("-> " + photo)


# ********************************************************************
# HELPER FUNCTIONS...
# ********************************************************************


def printSizeOfDataToBeHidden(num_bits):
    """
    Given the total number of bits, prints the size of the data to be hidden in a more human-readable format
    and prompts the user with the option of if they still want to continue with the data hiding process.
    :param num_bits: The number of bits that will be converted into a more human-readable format.
    """
    num_bytes = num_bits / 8
    dataTypeStr = ""

    if num_bytes < 1000:
        dataTypeStr = " bytes."
    elif num_bytes < 10 ** 6:
        dataTypeStr = " kilobytes."
        num_bytes = (num_bytes // 100) / 10
    elif num_bytes < 10 ** 9:
        dataTypeStr = " megabytes."
        num_bytes = (num_bytes // 10 ** 5) / 10
    elif num_bytes < 10 ** 12:
        dataTypeStr = " gigabytes."
        num_bytes = (num_bytes // 10 ** 8) / 10
    else:
        dataTypeStr = " terabytes."
        num_bytes = (num_bytes // 10 ** 11) / 10

    print("Size of data to be hidden: " + str(num_bytes) + dataTypeStr)
    print("Do you wish to continue?")
    answer = input()

    if answer[0] != 'y' and answer[0] != 'Y':
        print("No new images have been modified/saved. Goodbye.")
        sys.exit(0)

    print("***")


def checkIfDataCanBeHidden(num_bits, path_to_input_photos):
    """
    Checks to see if the number of bits to be hidden will be able to fit inside the specified set of photos.
    :param num_bits: The number of bits that have been requested to be hidden.
    :param path_to_input_photos: The path to the photos, whose sizes will be calculated to see if the given
    number of bits can fit inside the given set of photos.
    """
    capacity = getMaxDataThatCanBeHidden(path_to_input_photos, num_bits)

    # All data must be able to fit inside image(s)
    if num_bits > capacity:
        print("Error - Not enough space is available to store requested data in specified photo(s).")
        print("Your requested capacity: " + str(num_bits / 8) + " bytes.")
        print("Maximum capacity allowed: " + str(capacity / 8) + " bytes.")
        sys.exit(1)
    
    # Such an event would require roughly 2.3 million terabytes of data or more to be hidden... but you can never be too safe!!
    if num_bits >= 2 ** 64:
        print("Sorry, but you are dealing with an astronomical amount of data. Unable to process.")
        sys.exit(1)


def getNumBitsAvailableToHide(photo_name, photo_ID_reserve_bits, total_bits_reserve_bits, first_image):
    """
    Gets the total number of bits that can be hidden inside of a given photo (Minus the reserve bits).
    :param photo_name: The path to the photo that will be calculated.
    :param photo_ID_reserve_bits: The total number of bits that must be reserved for the storage of the
    photo identification number inside the given photo.
    :param total_bits_reserve_bits: The total number of bits that must be reserved for the storage of the
    total number of bits that will be hidden and stored in the set of photos. (These bits will only be 
    hidden inside of the first image that gets processed.)
    :param first_image: A boolean value indicating whether or not the given photo is recognized as the
    first image. 
    :return: The maximum number of bits of hidden data that the photo is able to store.
    """
    # Path must lead to a png image
    if not photo_name.lower().endswith('.png'):
        print("Error - Only png images are supported for this application.")
        print(str(os.path.basename(photo_name)) + " is not a png image.")
        sys.exit(1)

    image = Image.open(photo_name)
    width, height = image.size
    image.close()

    pixel_count = width * height

    # The first image must contain a bit extra data
    if first_image:
        val = pixel_count * 3 - 10 - photo_ID_reserve_bits - total_bits_reserve_bits
    else:
        val = pixel_count * 3 - 4 - photo_ID_reserve_bits

    if val <= 0:
        print("Error - Image size for " + str(os.path.basename(photo_name)) + " is way too small and is therefore unable to hide any data.")
        sys.exit(1)
    
    return val


def getMaxDataThatCanBeHidden(path_to_input_photos, total_bits):
    """
    Gets the maximum amount of data that can be hidden inside a given set of photos.
    :param path_to_input_photos: The path to the folder containing the set of photos.
    :param total_bits: The total number of bits of data that will be hidden (not including reserve bits).
    :return: The maximum size of data (in bits) that can be hidden in the given set of photos.
    """
    # Path must lead to a folder
    if not os.path.isdir(path_to_input_photos):
        print("Error - Specified path to folder containing photos does not lead to a folder.")
        sys.exit(1)
    
    # Sometimes unwanted hidden files may appear, which we do not want
    removePotentialHiddenFiles(path_to_input_photos)

    max_allowed_bits = 0
    num_photos_in_directory = len(os.listdir(path_to_input_photos))

    # There must exist at least one photo
    if num_photos_in_directory == 0:
        print("Error - You do not have any photos listed.")
        sys.exit(1)

    # Number of photos in path cannot exceed max number able to be stored in reserved bit space
    if num_photos_in_directory >= 2 ** 16:
        print("Error - Too many photos. Max is " + str(2 ** 16) - 1)
        sys.exit(1)
    
    # Calculate reserve bits
    photo_ID_reserve_bits = Miscellaneous_Helpers.getNumBitsToReserve(num_photos_in_directory)
    total_bits_reserve_bits = Miscellaneous_Helpers.getNumBitsToReserve(total_bits)

    first_image = True
    for photo in os.listdir(path_to_input_photos):
        photo_path = os.path.join(path_to_input_photos, photo)
        num = getNumBitsAvailableToHide(photo_path, photo_ID_reserve_bits, total_bits_reserve_bits, first_image)
        first_image = False

        # Super rare occurrence except for EXTREMELY small images (containing only a couple of pixels)
        if num < 1:
            print("Error - Image size for " + str(photo) + " is way too small.")
            sys.exit(1)

        max_allowed_bits += num

    return max_allowed_bits


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
            if item.startswith('.'):
                os.remove(item_path)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def storeDataInPixels(data, w, h, i, image):
    """
    Stores a specific set of bits inside of the pixels of a given image.
    :param data: The data, represented in bits, that is to be stored inside the image.
    :param w: The current pixel width value to start storing data at.
    :param h: The current pixel height value to start storing data at.
    :param i: The current index value, representing the number of bits that have currently 
    been stored so far in the given image.
    :param image: The image object containing all the pixel data of the current image.
    :return: A tuple containing the pixel width and height values, as well as the index i.
    """
    width, height = image.size

    for j in range(len(data)):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Image size is not large enough to store all initial necessary components.")
                image.close()
                sys.exit(1)
    
        rgb = list(image.getpixel((w, h)))

        # If true, then the current lsb pixel value needs to be changed
        if rgb[i%3] % 2 != data[j]:
            if data[j] == 0:
                rgb[i%3] -= 1
            else:
                rgb[i%3] += 1

        image.putpixel((w, h), tuple(rgb))

        i += 1

        # The RGB values for the current pixel have all been gone through and it's now time for the next pixel
        if i % 3 == 0:
            w += 1
    
    return (w, h, i)


def storeMainDataInPixels(bits, val, w, h, i, image, path_to_processed_photos, image_name):
    """
    All actual data meant to get hidden is stored here.
    :param bits: The data, represented in bits, that is to be stored inside the image.
    :param val: The total current index value, representing the TOTAL number of bits that have so far been stored 
    in any previously processed photos from this session, minus the number of reserve bits for this photo.
    :param w: The current pixel width value to start storing data at.
    :param h: The current pixel height value to start storing data at.
    :param i: The current index value, representing the number of bits that have currently been stored so far in
    the given image.
    :param image: The image object containing all the pixel data of the current image.
    :param path_to_processed_photos: The path to the location to store all photos that have been processed.
    :param image_name: The base name of the current photo being processed. The processed photo will have this
    same name and will then be stored in 'path_to_processed_photos'.
    :return: The new value of the current index value, i
    """
    width, height = image.size

    # Go through potential remaining G/B values in current pixel to start with fresh new pixel
    while i % 3 != 0:
        if i + val >= len(bits):
            image.save(os.path.join(path_to_processed_photos, image_name))
            return i
        
        rgb = list(image.getpixel((w, h)))

        if rgb[i%3] % 2 != bits[i + val]:
            if bits[i + val] == 0:
                rgb[i%3] -= 1
            else:
                rgb[i%3] += 1
        
        image.putpixel((w, h), tuple(rgb))
        
        i += 1
    
    w += 1

    # Go through all remaining pixels in photo (or until all data has been stored)
    for h in range(h, height):
        for w in range(w, width):
            for j in range(3):
                if i + val >= len(bits):
                    image.save(os.path.join(path_to_processed_photos, image_name))
                    return i

                rgb = list(image.getpixel((w, h)))

                if rgb[i%3] % 2 != bits[i + val]:
                    if bits[i + val] == 0:
                        rgb[i%3] -= 1
                    else:
                        rgb[i%3] += 1
        
                image.putpixel((w, h), tuple(rgb))
                
                i += 1
        w = 0
    
    return i

def hideDataInPhoto(bits, current_index, photo, photo_ID, total_bits, first_image, path_to_processed_photos):
    """
    Hides all data needed to be hidden in the current given photo.
    :param bits: The data, represented in bits, that is to be stored inside the image.
    :param current_index: The total current index value, representing the TOTAL number of bits that have so far been stored 
    in any previously processed photos from this session.
    :param photo: The path to the current photo to be processed.
    :param photo_ID: The photo ID number (in bit format) that will be stored in the current photo to be processed. 
    :param total_bits: The total number of bits of data that will be hidden (not including reserve bits).
    :param first_image: A boolean value indicating whether or not the given photo is recognized as the
    first image. 
    :param path_to_processed_photos: The path to the location to store all photos that have been processed.
    :return: The start of the next current bit index for the next potential photo to be processed.
    """
    image = Image.open(photo)

    print("Currently hiding data in photo " + str(os.path.basename(photo)) + "  (" + str((current_index * 1000 // len(bits)) / 10) + "% complete)")

    # Convert the image to RGB color mode if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    total_reserve_bits = 4 + len(photo_ID) if not first_image else 10 + len(photo_ID) + len(total_bits)
    
    width, height = image.size

    w = 0
    h = 0

    i = 0

    # Store number of bits to reserve for photo ID num (minus one)
    bit_ID_length = DecimalBitConverters.convertDecimalToBits(len(photo_ID) - 1, 4)
    w, h, i = storeDataInPixels(bit_ID_length, w, h, i, image)

    # Store photo ID num
    w, h, i = storeDataInPixels(photo_ID, w, h, i, image)
    
    # Storing total number of bits to be stored is only done in the first photo
    if first_image:
        # Store number of bits to reserve for total num of bits (minus one)
        bit_total_bits_length = DecimalBitConverters.convertDecimalToBits(len(total_bits) - 1, 6)
        w, h, i = storeDataInPixels(bit_total_bits_length, w, h, i, image)
        
        # Store number of total bits to be stored
        w, h, i = storeDataInPixels(total_bits, w, h, i, image)
    
    # Now we can store all hidden data! Hooray!
    val = current_index - total_reserve_bits
    i = storeMainDataInPixels(bits, val, w, h, i, image, path_to_processed_photos, os.path.basename(photo))
    
    image.save(os.path.join(path_to_processed_photos, os.path.basename(photo)))
    
    return i + val