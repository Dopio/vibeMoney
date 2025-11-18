import pytesseract
from PIL import Image
import os


def check_tesseract():
    print("🔍 ПРОВЕРКА TESSERACT")
    print("=" * 50)

    print(f"📁 Путь к tesseract: {pytesseract.pytesseract.tesseract_cmd}")
    print(f"📁 Файл существует: {os.path.exists(pytesseract.pytesseract.tesseract_cmd)}")

    # Создаем тестовое изображение с текстом
    test_text = "+34 to Accuracy Rating"
    print(f"📝 Тестовый текст: '{test_text}'")

    # Пробуем распознать
    try:
        # Создаем простое изображение с текстом
        from PIL import ImageDraw, ImageFont

        img = Image.new('RGB', (300, 50), color='white')
        draw = ImageDraw.Draw(img)

        # Пробуем разные шрифты
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()

        draw.text((10, 10), test_text, fill='black', font=font)
        img.save('test_accuracy_text.png')

        text = pytesseract.image_to_string(img, lang='eng')
        print(f"✅ Tesseract распознал: '{text.strip()}'")

    except Exception as e:
        print(f"❌ Ошибка Tesseract: {e}")


if __name__ == "__main__":
    check_tesseract()
