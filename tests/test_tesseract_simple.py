# test_tesseract_simple.py
import pytesseract
from PIL import Image
import os

print("Tesseract путь:", pytesseract.pytesseract.tesseract_cmd)
print("Файл существует:", os.path.exists(pytesseract.pytesseract.tesseract_cmd))

# Простой тест
try:
    image = Image.new('RGB', (100, 100), color='white')
    text = pytesseract.image_to_string(image)
    print("✅ Tesseract работает")
except Exception as e:
    print("❌ Tesseract ошибка:", e)
