import pytesseract
from PIL import Image
import os

class OCREngine:
    def __init__(self, tesseract_cmd=None):
        """
        Initialize the OCR Engine.
        :param tesseract_cmd: Optional path to tesseract executable.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_path):
        """
        Extracts text from an image using Tesseract OCR.
        :param image_path: Path to the image file.
        :return: Extracted text string.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error during OCR extraction: {e}")
            return ""
