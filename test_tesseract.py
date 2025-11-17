import pytesseract
from PIL import Image, ImageDraw, ImageFont

# Попробуем автоматическое обнаружение
try:
    # Создаем тестовое изображение с текстом
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    draw.text((50, 30), "Hello Tesseract OCR!", fill='black', font=font)
    img.save('test_ocr.png')

    # Пробуем распознать
    text = pytesseract.image_to_string(img, lang='eng')
    print("✅ Tesseract работает!")
    print(f"Распознанный текст: '{text.strip()}'")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("Пробуем указать путь вручную...")

    # Указываем путь вручную
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(img, lang='eng')
        print("✅ Tesseract работает с ручным путем!")
        print(f"Распознанный текст: '{text.strip()}'")

        # Сохраняем настройку в scanner.py
        with open('core/scanner.py', 'r', encoding='utf-8') as f:
            content = f.read()

        if 'pytesseract.pytesseract.tesseract_cmd' not in content:
            with open('core/scanner.py', 'w', encoding='utf-8') as f:
                f.write('import pytesseract\n')
                f.write(
                    'pytesseract.pytesseract.tesseract_cmd = r\'C:\\Program Files\\Tesseract-OCR\\tesseract.exe\'\n\n')
                f.write(content)
            print("✅ Путь добавлен в scanner.py")

    except Exception as e2:
        print(f"❌ Tesseract не найден: {e2}")
        print("Скачай Tesseract с: https://github.com/UB-Mannheim/tesseract/wiki")
