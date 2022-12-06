
import pytesseract
import cv2
from text_to_speech import speak
image = cv2.imread('sampleImages/4.PNG')
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
text = pytesseract.image_to_string(image)
print(text)
speak(text)
