from Data_Converters import ByteDataToDirectory, DecimalBitConverters, BinaryByteConverters
from PIL import Image
import pickle, os, sys, math, shutil


def extractDataFromImages(processed_photos, path_to_paste_data):
    # Any previously extracted data will get removed before adding the newly extracted data
    removePreviouslyExtractedData(path_to_paste_data)
    
    photo_dict = createPhotoDictionary(processed_photos)
    bits = getAllBinaryDataFromPhotos(photo_dict)
    
    byte_data_list = BinaryByteConverters.convertFullBinaryToByteDataList(bits)
    ByteDataToDirectory.createDirectoryFromByteData(path_to_paste_data, byte_data_list)

    print("Success! The data from the image set has been extracted and can now be viewed. (100% complete)")


def getAllBinaryDataFromPhotos(photo_dict):
    bits = bytearray()
    total_bit_data_size = getTotalBitsNumDataSize(photo_dict[0], 4 + getNumBitsToReserve(getImageNum(photo_dict[0])))

    # Extract all hidden data from all images
    for i in range(len(photo_dict)):
        bits += extractDataFromImage(photo_dict[i], len(bits), total_bit_data_size)
    
    if len(bits) != total_bit_data_size:
        print("Error - Unable to process photo(s) as it may be prone to errors")
        sys.exit(1)

    return bits


def getNumBitsToReserve(num):
    return math.ceil(math.log2(num + 1)) if num > 0 else 1


def removePreviouslyExtractedData(extracted_data_path):
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


def getStartBitsDataLength(image_path):
    image_num = getImageNum(image_path)
    image_num_data_length = 4 + getNumBitsToReserve(image_num)

    # All additional photos after the first photo only store the image number data as their precursor
    if image_num != 0:
        return image_num_data_length
    
    stored_bit_data_size = getTotalBitsNumDataSize(image_path, image_num_data_length)

    return image_num_data_length + 6 + getNumBitsToReserve(stored_bit_data_size)
    

def getTotalBitsNumDataSize(image_path, precursor_bit_length):
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
    for j in range(precursor_bit_length):
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
    
    b_total_size_length = bytearray()
    for j in range(6):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Invalid image for data extraction.")
                print("Image " + str(os.path.basename(photo_path)) + " is too small and therefore could've never stored any data in the first place.")
                image.close()
                sys.exit(1)
        
        rgb = image.getpixel((w, h))

        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        b_total_size_length.append(bVal[7])

        i += 1
    
        if i % 3 == 0:
            w += 1
    
    total_size_length = 1 + DecimalBitConverters.convertBitsToDecimal(b_total_size_length)
    
    b_bit_data_size = bytearray()
    for j in range(total_size_length):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Invalid image for data extraction.")
                print("Image " + str(os.path.basename(photo_path)) + " is too small and therefore could've never stored any data in the first place.")
                image.close()
                sys.exit(1)
        
        rgb = image.getpixel((w, h))

        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        b_bit_data_size.append(bVal[7])

        i += 1
    
        if i % 3 == 0:
            w += 1
    
    return DecimalBitConverters.convertBitsToDecimal(b_bit_data_size)


def createPhotoDictionary(processed_photos):
    photo_dict = {}

    # Fill the dictionary with the photos and their corresponding identifier numbers
    for photo in os.listdir(processed_photos):
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
    aList = []
    for i in range(max + 1):
        aList.append(i)
    
    return aList


def extractDataFromImage(image_path, current_num_bits_extracted, total_bit_data_size):
    print("Currently extracting data from photo " + str(os.path.basename(image_path)), end="")
    print("  (" + str((current_num_bits_extracted * 1000 // total_bit_data_size) / 10) + "% complete)")

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
    # since we will not be dealing with this.
    for j in range(precursor_bit_length):
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
    
    # Go through any potential remaining green and/or blue values in the current pixel, if any so that we can later start
    # with a fresh new pixel.
    while i % 3 != 0:
        rgb = image.getpixel((w, h))

        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        bits.append(bVal[7])
        
        i += 1
        current_num_bits_extracted += 1
         
        # All data hidden in image(s) has been read, meaning any future remaining pixels do not need to be explored since they never got modified.
        if current_num_bits_extracted == total_bit_data_size:
            image.close()
            return bits
    
    w += 1

    for h in range(h, height):
        for w in range(w, width):
            for j in range(3):
                rgb = image.getpixel((w, h))

                bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
                bits.append(bVal[7])
                
                i += 1
                current_num_bits_extracted += 1

                # All data hidden in image(s) has been read
                if current_num_bits_extracted == total_bit_data_size:
                    image.close()
                    return bits

        w = 0
    
    # Future bits in the image have been explored when they shouldn't have
    if current_num_bits_extracted > total_bit_data_size:
        print("Error in extracting data from photo " + str(os.path.basename(image_path)))
        sys.exit(1)
    
    image.close()

    return bits


def getImageNum(photo_path):
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
    for j in range(4):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Invalid image for data extraction.")
                print("Image " + str(os.path.basename(photo_path)) + " is too small and therefore could've never stored any data in the first place.")
                image.close()
                sys.exit(1)
        
        rgb = image.getpixel((w, h))

        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        b_ID_length.append(bVal[7])

        i += 1
    
        # The RGB values for the current pixel have all been gone through and it's now time for the next pixel
        if i % 3 == 0:
            w += 1
    
    # ID length stored in first pixel and 1/3 of second is one less than the actual length, so we then add one when computing the actual length.
    # This allows us to store twice as many photos (Max: 2^16 = 65536 instead of 2^15 = 32768)
    ID_length = 1 + DecimalBitConverters.convertBitsToDecimal(b_ID_length)

    b_photo_num = bytearray()
    for j in range(ID_length):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Invalid image for data extraction.")
                print("Image " + str(os.path.basename(photo_path)) + " is too small and therefore could've never stored any data in the first place.")
                image.close()
                sys.exit(1)
        
        rgb = image.getpixel((w, h))

        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        b_photo_num.append(bVal[7])

        i += 1
    
        if i % 3 == 0:
            w += 1
    
    image.close()
    
    return DecimalBitConverters.convertBitsToDecimal(b_photo_num)
        



