# bizcardX_extracting_buisness_card_with_OCR
**BizCardX: Extracting Business Card Data with OCR**

Bizcard Extraction is a Python application built with Streamlit, EasyOCR, Regex function, and POSTGRESQL database. It allows users to extract information from business cards and store it in a POSTGRESQL  database for further analysis. The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.

# What is EasyOCR?

EasyOCR, as the name suggests, is a Python package that allows computer vision developers to effortlessly perform Optical Character Recognition.It is a Python library for Optical Character Recognition (OCR) that allows you to easily extract text from images and scanned documents. In my project I am using easyOCR to extract text from business cards.

When it comes to OCR, EasyOCR is by far the most straightforward way to apply Optical Character Recognition:

    *The EasyOCR package can be installed with a single pip command.
    *The dependencies on the EasyOCR package are minimal, making it easy to configure your OCR development environment.
    *Once EasyOCR is installed, only one import statement is required to import the package into your project.
    *From there, all you need is two lines of code to perform OCR — one to initialize the Reader class and then another to OCR the image via the readtext function.

# Libraries/Modules used for the project!

    *Pandas - (To Create a DataFrame with the scraped data)
    *POSTGRESQL - (To store and retrieve the data)
    *Streamlit - (To Create Graphical user Interface)
    *EasyOCR - (To extract text from images)
    
# Features

    Extracts text information from business card images using EasyOCR. 
    Uses regular expressions (RegEx) to parse and extract specific fields like name, designation, company, contact details, etc.
    Stores the extracted information in a POSTGRESQL database for easy retrieval and analysis.
    Provides a user-friendly interface built with Streamlit to upload images, extract information, and view/update the database.
    
