from Data_Converters import DirectoryToByteData, BinaryByteConverters, DecimalBitConverters
from PIL import Image
import pickle, sys, os, math


def hideDataInImages(folder_path, path_to_input_photos, path_to_processed_photos):
    byte_data_list = DirectoryToByteData.getByteData(folder_path)
    bits = BinaryByteConverters.convertByteDataListToFullBinary(byte_data_list)

    # All error checking happens here to determine whether or not photo data can properly be hidden
    checkIfDataCanBeHidden(bits, path_to_input_photos)

    printSizeOfDataToBeHidden(len(bits))

    # Any processed photos from a previous session will get removed
    removePreviouslyExtractedData(path_to_processed_photos)

    # Total number of bits to be hidden in binary (bit) format
    b_total_bits = DecimalBitConverters.convertDecimalToBits(len(bits), getNumBitsToReserve(len(bits)))

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

        b_photo_num = DecimalBitConverters.convertDecimalToBits(photo_num, getNumBitsToReserve(photo_num))

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


def printSizeOfDataToBeHidden(num_bits):
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


def checkIfDataCanBeHidden(bits, path_to_input_photos):
    capacity = getMaxDataThatCanBeHidden(path_to_input_photos, len(bits))

    # All data must be able to fit inside image(s)
    if len(bits) > capacity:
        print("Error - Not enough space is available to store requested data in specified photo(s).")
        print("Your requested capacity: " + str(len(bits) / 8) + " bytes.")
        print("Maximum capacity allowed: " + str(capacity / 8) + " bytes.")
        sys.exit(1)
    
    # Such an event would require roughly 2.3 million terabytes of data or more to be hidden... but you can never be too safe!!
    if len(bits) >= 2 ** 64:
        print("What the heck are you trying to hide?! You are dealing with an astronomical amount of data. Sorry, unable to process.")
        sys.exit(1)


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


def getNumBitsAvailableToHide(photo_name, photo_ID_reserve_bits, total_bits_reserve_bits, first_image):
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
    photo_ID_reserve_bits = getNumBitsToReserve(num_photos_in_directory)
    total_bits_reserve_bits = getNumBitsToReserve(total_bits)

    first_image = True
    for photo in os.listdir(path_to_input_photos):
        photo_path = os.path.join(path_to_input_photos, photo)
        num = getNumBitsAvailableToHide(photo_path, photo_ID_reserve_bits, total_bits_reserve_bits, first_image)
        first_image = False

        # Super rare occurrence except for EXTREMELY small images
        if num < 1:
            print("Error - Image size for " + str(photo) + " is way too small.")
            sys.exit(1)

        max_allowed_bits += num

    return max_allowed_bits


def getNumBitsToReserve(num):
    return math.ceil(math.log2(num + 1)) if num > 0 else 1


def removePotentialHiddenFiles(folder_path):
    try:
        folder_contents = os.listdir(folder_path)
        
        for item in folder_contents:
            item_path = os.path.join(folder_path, item)
            
            # Check if the item is a hidden file (starts with a dot)
            if item.startswith('.'):
                os.remove(item_path)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def hideDataInPhoto(bits, current_index, photo, photo_ID, total_bits, first_image, path_to_processed_photos):
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
    for j in range(4):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Image size is not large enough to store all initial necessary components.")
                image.close()
                sys.exit(1)
        
        rgb = list(image.getpixel((w, h)))

        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        bVal[7] = bit_ID_length[j]

        rgb[i%3] = DecimalBitConverters.convertBitsToDecimal(bVal)
        image.putpixel((w, h), tuple(rgb))

        i += 1

        # The RGB values for the current pixel have all been gone through and it's now time for the next pixel
        if i % 3 == 0:
            w += 1
    
    # Store photo identifier num
    for j in range(len(photo_ID)):
        if w >= width:
            w = 0
            h += 1
            if h >= height:
                print("Error - Image size is not large enough to store all initial necessary components.")
                image.close()
                sys.exit(1)
        
        rgb = list(image.getpixel((w, h)))
        
        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        bVal[7] = photo_ID[j]
        
        rgb[i%3] = DecimalBitConverters.convertBitsToDecimal(bVal)
        image.putpixel((w, h), tuple(rgb))

        i += 1
        
        if i % 3 == 0:
            w += 1
    
    # Storing total number of bits to be stored is only done in the first photo
    if first_image:
        # Store number of bits to reserve for total num of bits (minus one)
        bit_total_bits_length = DecimalBitConverters.convertDecimalToBits(len(total_bits) - 1, 6)
        for j in range(6):
            if w >= width:
                w = 0
                h += 1
                if h >= height:
                    print("Error - Image size is not large enough to store all initial necessary components.")
                    image.close()
                    sys.exit(1)

            rgb = list(image.getpixel((w, h)))
            
            bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
            bVal[7] = bit_total_bits_length[j]
            
            rgb[i%3] = DecimalBitConverters.convertBitsToDecimal(bVal)
            image.putpixel((w, h), tuple(rgb))
            
            i += 1

            if i % 3 == 0:
                w += 1
        
        # Store number of total bits to be stored
        for j in range(len(total_bits)):
            if w >= width:
                w = 0
                h += 1
                if h >= height:
                    print("Error - Image size is not large enough to store all initial necessary components.")
                    image.close()
                    sys.exit(1)
            
            rgb = list(image.getpixel((w, h)))
            
            bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
            bVal[7] = total_bits[j]

            rgb[i%3] = DecimalBitConverters.convertBitsToDecimal(bVal)
            image.putpixel((w, h), tuple(rgb))

            i += 1
            
            if i % 3 == 0:
                w += 1
    
    # Now we can store all hidden data! Hooray!
    val = current_index - total_reserve_bits

    # Go through any potential remaining green and/or blue values in the current pixel, if any so that we can later start
    # with a fresh new pixel.
    while i % 3 != 0:
        if i + val >= len(bits):
            image.save(os.path.join(path_to_processed_photos, os.path.basename(photo)))
            return i + val
        
        rgb = list(image.getpixel((w, h)))
        
        bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
        bVal[7] = bits[i + val]
        
        rgb[i%3] = DecimalBitConverters.convertBitsToDecimal(bVal)
        image.putpixel((w, h), tuple(rgb))
        
        i += 1
    
    w += 1

    for h in range(h, height):
        for w in range(w, width):
            for j in range(3):
                if i + val >= len(bits):
                    image.save(os.path.join(path_to_processed_photos, os.path.basename(photo)))
                    return i + val

                rgb = list(image.getpixel((w, h)))

                bVal = DecimalBitConverters.convertDecimalToBits(rgb[i%3], 8)
                bVal[7] = bits[i + val]
                rgb[i%3] = DecimalBitConverters.convertBitsToDecimal(bVal)
                
                image.putpixel((w, h), tuple(rgb))
                
                i += 1

        w = 0
    
    image.save(os.path.join(path_to_processed_photos, os.path.basename(photo)))
    
    return i + val