# My Project

This program enables users to conceal a wide range of data within one or multiple photos. This 
includes, but is not limited to, text, PDFs, sound files, images, and even entire Minecraft 
worlds. The technique used is called steganography, where data is hidden in plain sight, 
imperceptible to the naked eye. In our case, data is converted into bit format and discreetly
stored in the least significant bits of the red, green, and blue color values of each pixel. 
Retrieving this hidden data requires both knowledge of its presence in the image(s) and the use 
of the appropriate extraction technology, which is also available here.

## Installation

To use this project on your local machine, clone this repository and install any dependencies in
requirements.txt (You can use the command "pip install -r requirements.txt")

## Usage

After installing all required components, modify the main.py file to include the path to the file or
folder that you wish to hide (under variable name 'path_to_data_you_want_hidden'). Next, add one or 
multiple png images inside of the 'Input_Photos' folder. Depending on the size of the data you are
trying to hide, you may need more than one photo to store all of the hidden data. 

To run the program, type in the command, 'python3 main.py' or 'python main.py' via terminal in the 
project's root directory. 

***

Hiding Data:

After running the project, enter '1' when instructed to do so. Each png image inside
of 'Input_Photos' will be copied, and the copied version will be modified to store all hidden data 
that can fit inside the image. Each newly modified image will then appear in the 'Processed_Photos'
folder. Note that not all images in 'Input_Photos' will need to be processed if the hidden data is
able to fit in fewer images. Also note that if the hidden data is too large, the program will stop
before any images can be copied and modified.

***

Extracting Data:

When extracting all hidden data and recreating it to its previous format, make sure that all previously
processed photo(s) containing the data are located in the 'Processed_Photos' folder. Data will be
extracted and recreated if and only if all processed photos from a previous session have been included
(and those photos only). Next, rerun the project, this time entering '2' when instructed to do so to 
start the data extraction process. When complete, you should see your recreated data in its previous
format, located in the 'Extracted_Data' folder.

***

Note that this project was made to work with Python3 version 3.11.2 so any other versions may or may
not work as expected. Also, this project is meant for educational purposes only and shall not be used
for any illegal activity and/or activity that could directly or indirectly cause harm to others. 

## Contributing

If you want to be a contributor, feel free to submit a pull request! If your request gets denied, you may
still modify a copy of this repository as you wish and use it for any of your personal projects. If you
notice any bugs, report them to anyissuereports@gmail.com

## License

This project is licensed under the [MIT License](LICENSE).

## Author

Asa Barton

## Acknowledgments

This project was inspired by Charles Keith, also known online as NetworkChuck, who runs a successful Youtube 
channel and had published a video regarding steganography (https://youtu.be/sLkdtjJc6mc?si=wIM_xJdaD02WuTUn), 
from which I drew my inspiration.