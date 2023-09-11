from Data_Converters import ByteDataToDirectory, DecimalBitConverters, BinaryByteConverters, Miscellaneous_Helpers
from PIL import Image
import pickle, os, sys, math, shutil


def extractDataFromImages(processed_photos, path_to_paste_data):
    """
    Extracts all hidden data from a given set of images and reconstructs the data back to its original form.
    :param processed_photos: Path to the folder containing all photos which contain hidden data.
    :param path_to_paste_data: Path to the folder where the hidden data will be reconstructed and stored.
    """
    # Any previously extracted data will get removed before adding the newly extracted data
    Miscellaneous_Helpers.removePreviouslyExtractedData(path_to_paste_data)
    
    photo_dict = createPhotoDictionary(processed_photos)
    bits = getAllBinaryDataFromPhotos(photo_dict)
    
    byte_data_list = BinaryByteConverters.convertFullBinaryToByteDataList(bits)
    ByteDataToDirectory.createDirectoryFromByteData(path_to_paste_data, byte_data_list)

    print("Success! The data from the image set has been extracted and can now be viewed. (100% complete)")


# ********************************************************************
# HELPER FUNCTIONS...
# ********************************************************************


def getAllBinaryDataFromPhotos(photo_dict):
    """
    Extracts all the binary data hidden inside a given set of photos.
    :param photo_dict: A dictionary of photos, where the key is the photo's identifier number and the value
    is the name of the path to the photo.
    :return: All of the extracted hidden data represented as a string of bits.
    """
    bits = bytearray()
    total_bit_data_size = getTotalBitsNumDataSize(photo_dict[0], 4 + Miscellaneous_Helpers.getNumBitsToReserve(getImageNum(photo_dict[0])))

    # Extract all hidden data from all images
    for i in range(len(photo_dict)):
        bits += extractDataFromImage(photo_dict[i], len(bits), total_bit_data_size)
    
    if len(bits) != total_bit_data_size:
        print("Error - Unable to process photo(s) as it may be prone to errors")
        sys.exit(1)

    return bits


def getStartBitsDataLength(image_path):
    """
    Gets the total number of reserve bits that are present in a given photo.
    :param image_path: The path to the current image containing a certain number of reserve bits.
    :return: The total number of reserve bits present in the given image.
    """
    image_num = getImageNum(image_path)
    image_num_data_length = 4 + Miscellaneous_Helpers.getNumBitsToReserve(image_num)

    # All additional photos after the first photo only store the image number data as their precursor
    if image_num != 0:
        return image_num_data_length
    
    stored_bit_data_size = getTotalBitsNumDataSize(image_path, image_num_data_length)

    return image_num_data_length + 6 + Miscellaneous_Helpers.getNumBitsToReserve(stored_bit_data_size)


def iterateOverBitImageVals(length, i, w, h, image, photo_path):
    """
    Iterates over a specified number of bits inside the image. No pixel values are changed and no data is extracted.
    :param length: The number of bits to iterate through (number of RGB pixel values)
    :param i: The current index value, representing the number of bits that have currently been gone over so far in
    the given image.
    :param w: The current image pixel width value being looked at.
    :param h: The current image pixel height value being looked at.
    :param image: The image object containing all the pixel data of the current image.
    :param photo_path: The path to the photo whose pixel values are being iterated over.
    :return: The updated values of i, w, and h.
    """
    width, height = image.size

    for j in range(length):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Invalid image for data extraction.")
                print("Image " + str(os.path.basename(photo_path)) + " is too small and therefore could've never stored any data in the first place.")
                image.close()
                sys.exit(1)

        i += 1
    
        # The RGB values for the current pixel have all been gone through and it's now time for the next pixel
        if i % 3 == 0:
            w += 1
    
    return (i, w, h)


def getPixelVals(length, extracted_bits, i, w, h, image, photo_path):
    """
    Gets all of the image pixel least significant bit values within a specified range (i to i + length - 1)
    :param length: The number of pixel value bits to extract from the given image.
    :param extracted_bits: All hidden bits get extracted and stored in this data structure (a list of 0's and 1's)
    :param i: The current index value, representing the number of bits that have currently been gone over so far in
    the given image.
    :param w: The current image pixel width value being looked at.
    :param h: The current image pixel height value being looked at.
    :param image: The image object containing all the pixel data of the current image.
    :param photo_path: The path to the photo whose pixel lsb values are being extracted and stored.
    :return: The updated values of i, w, and h.
    """
    width, height = image.size

    for j in range(length):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Invalid image for data extraction.")
                print("Image " + str(os.path.basename(photo_path)) + " is too small and therefore could've never stored any data in the first place.")
                image.close()
                sys.exit(1)
        
        rgb = image.getpixel((w, h))
        extracted_bits.append(rgb[i%3] % 2)

        i += 1
    
        if i % 3 == 0:
            w += 1
    
    return (i, w, h)


def getTotalBitsNumDataSize(image_path, precursor_bit_length):
    """
    Gets the number of bits reserved for storing the total number of bits of data that has been hidden (Stored num only in first image)
    :param image_path: The path to the image containing the number of bits of data that has been hidden.
    :param precursor_bit_length: The number of image pixel value bits that need to be iterated over before we get to the bits in the
    image used to store the value we are looking for.
    :return: The total number of bits that have been hidden in a photo set (which we have found, hidden in our given image).
    """
    # Only the image that has image number 0 can be inputted into this function
    if getImageNum(image_path) != 0:
        print("Error - Image " + str(os.path.basename(image_path)) + " is an invalid image for extracting total number of bits.")
        sys.exit(1)

    image = Image.open(image_path)

    # Convert the image to RGB color mode if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    width, height = image.size
    
    w = 0
    h = 0

    i = 0

    # Iterate over starting bit values in image containing image num data since we will currently not be dealing with this
    i, w, h = iterateOverBitImageVals(precursor_bit_length, i, w, h, image, image_path)
    
    # Obtaining the length (of the) length in bits of the total number of bits that are hidden
    b_total_size_length = bytearray()
    i, w, h = getPixelVals(6, b_total_size_length, i, w, h, image, image_path)
    total_size_length = 1 + DecimalBitConverters.convertBitsToDecimal(b_total_size_length)
    
    # Obtaining the length in bits of the total number of bits that are hidden
    b_bit_data_size = bytearray()
    i, w, h = getPixelVals(total_size_length, b_bit_data_size, i, w, h, image, image_path)
    
    return DecimalBitConverters.convertBitsToDecimal(b_bit_data_size)


def createPhotoDictionary(processed_photos):
    """
    Creates a dictionary of photos, where the keys are the extracted unique image identifier numbers that are mapped to their 
    corresponding photos.
    :param processed_photos: The path to the folder containing the processed photos which have data hidden in them.
    :return: The newly created dictionary of photos with their corresponding identifier numbers (keys). Note that in order to
    be valid, all keys must be a unique number from 0 to n - 1, where n is the total number of photos containing the hidden data.
    """
    photo_dict = {}

    Miscellaneous_Helpers.removePotentialHiddenFiles(processed_photos)

    # Fill the dictionary with the photos and their corresponding identifier numbers
    for photo in os.listdir(processed_photos):
        # Check to make sure only compatible image types being processed
        if not photo.lower().endswith('.png'):
            print("Error - Only png images are allowed for extraction.")
            sys.exit(1)

        photo_path = os.path.join(processed_photos, photo)
        current_num = getImageNum(photo_path)

        # Multiple separate photos cannot contain the same identifier number
        if current_num in photo_dict:
            print("Error - Invalid set of photos for extraction.")
            print("Photos '" + str(os.path.basename(photo_dict[current_num])) + "' and '" + photo + "' contain the same identifier number.")
            sys.exit(1)

        photo_dict[current_num] = photo_path

    nums = fillListWithNumbersFromZeroToMax(len(photo_dict) - 1)
    
    # Check that all photo identifier numbers are within proper range (0 to n - 1, where n is the number of photos to process)
    for key in photo_dict:
        if not key in nums:
            print("Error - Invalid set of photos for extraction.")
            print("Photo number for '" + str(os.path.basename(photo_dict[key])) + "' is not in range, given the current set of photos for extraction.")
            sys.exit(1)
        
        nums.remove(key)
    
    return photo_dict


def fillListWithNumbersFromZeroToMax(max):
    """
    Fills a list with integers from zero to max (size = max + 1)
    :param max: The largest (and last) integer value to be stored in the list.
    :return: The list containing integers zero to max.
    """
    aList = []
    for i in range(max + 1):
        aList.append(i)
    
    return aList


def getMainDataFromPixels(bits, i, w, h, image, current_num_extracted, total_bits):
    """
    Extracts all hidden data that will later be reconstructed.
    :param bits: Our bytearray data structure which stores all extracted bits.
    :param i: The current index value, representing the number of bits that have currently been gone over so far in
    the given image.
    :param w: The current image pixel width value being looked at.
    :param h: The current image pixel height value being looked at.
    :param image: The image object containing all the pixel data of the current image.
    :param current_num_extracted: The current number of bits that have so far been extracted from any potential
    previous images (not including reserve bits).
    :param total_bits: The total number of bits of data that have been hidden (In all images). This way we know 
    when to stop extracting least significant bit values.
    :return: The updated current number of bits that have been extracted.
    """
    width, height = image.size

    # Go through potential remaining G/B values in current pixel to start with fresh new pixel
    while i % 3 != 0:
        rgb = image.getpixel((w, h))
        bits.append(rgb[i%3] % 2)
        
        i += 1
        current_num_extracted += 1
         
        # All data hidden in image(s) has been read, meaning any future remaining pixels do not need to be explored since they never got modified.
        if current_num_extracted == total_bits:
            image.close()
            return current_num_extracted
    
    w += 1

    for h in range(h, height):
        for w in range(w, width):
            for j in range(3):
                rgb = image.getpixel((w, h))
                bits.append(rgb[i%3] % 2)
                
                i += 1
                current_num_extracted += 1

                # All data hidden in image(s) has been read
                if current_num_extracted == total_bits:
                    image.close()
                    return current_num_extracted
        w = 0
    
    return current_num_extracted


def extractDataFromImage(image_path, current_num_bits_extracted, total_bit_data_size):
    """
    Extracts all hidden data from a given image.
    :param image_path: The path to the image containing hidden data that will be extracted.
    :param current_num_bits_extracted: The current number of bits of data that have so far been 
    extracted from any potential previous images.
    :param total_bit_data_size: The total number of bits of data that have been hidden in an image
    set. This same number of bits needs to be extracted from all photos.
    :return: The updated bytearray data structure storing all extracted bits.
    """
    try:
        print("Currently extracting data from photo " + str(os.path.basename(image_path)), end="")
        print("  (" + str((current_num_bits_extracted * 1000 // total_bit_data_size) / 10) + "% complete)")
    except ZeroDivisionError as e:
        print("\nError - Invalid Photo")
        sys.exit(1)

    bits = bytearray()
    precursor_bit_length = getStartBitsDataLength(image_path)

    image = Image.open(image_path)

    # Convert the image to RGB color mode if needed
    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size

    w = 0
    h = 0

    i = 0

    # Iterate over starting bit values in image containing image num data (and data size if first image)
    i, w, h = iterateOverBitImageVals(precursor_bit_length, i, w, h, image, image_path) 
    
    # Extract the main data that will later be reconstructed from the remaining pixels
    current_num_bits_extracted = getMainDataFromPixels(bits, i, w, h, image, current_num_bits_extracted, total_bit_data_size)

    # Future bits in the image have been explored when they shouldn't have
    if current_num_bits_extracted > total_bit_data_size:
        print("Error in extracting data from photo " + str(os.path.basename(image_path)))
        sys.exit(1)
    
    image.close()

    return bits


def getImageNum(photo_path):
    """
    Obtains the image identifier number hidden in an image.
    :param photo_path: The path to the image containing an identifier number we wish toi extract.
    :return: The hidden image identifier number from the given image.
    """
    image = Image.open(photo_path)

    # Convert the image to RGB color mode if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    width, height = image.size

    w = 0
    h = 0

    i = 0

    # Extract the length, in bits, of the current photo ID number
    b_ID_length = bytearray()
    i, w, h = getPixelVals(4, b_ID_length, i, w, h, image, photo_path)
    ID_length = 1 + DecimalBitConverters.convertBitsToDecimal(b_ID_length)

    # Extract the actual photo ID num
    b_photo_num = bytearray()
    i, w, h = getPixelVals(ID_length, b_photo_num, i, w, h, image, photo_path)
    
    image.close()
    
    return DecimalBitConverters.convertBitsToDecimal(b_photo_num)
        
