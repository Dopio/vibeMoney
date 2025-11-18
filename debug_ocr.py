import sys
import os
import pytesseract
from PIL import ImageGrab, Image
import cv2
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def debug_ocr():
    print("🔍 ДИАГНОСТИКА OCR")
    print("=" * 50)

    # Область сканирования из вашего конфига
    scan_region = (2328, 493, 285, 65)  # x, y, width, height
    x, y, w, h = scan_region

    print(f"📐 Область: {scan_region}")
    print(f"📏 Размер: {w}x{h} пикселей")

    # 1. Захватываем скриншот
    print("\n📷 Захватываю скриншот...")
    screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))

    # Сохраняем оригинальный скриншот для отладки
    screenshot.save('debug_original.png')
    print("✅ Оригинальный скриншот: debug_original.png")

    # 2. Показываем что захватили
    print("\n🖼️ Предпросмотр области:")
    screenshot.show()  # Откроет изображение

    # 3. Пробуем разные настройки OCR
    configs = [
        r'--oem 3 --psm 6',
        r'--oem 3 --psm 7',  # Одна текстовая строка
        r'--oem 3 --psm 8',  # Одно слово
        r'--oem 3 --psm 13',  # Необработанный текст
    ]

    # Конвертируем в OpenCV для обработки
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Тестируем разные методы обработки
    methods = [
        ("Оригинал", img),
        ("Черно-белый", cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
        ("Высокий контраст", enhance_contrast(img)),
        ("Бинаризация", apply_threshold(img)),
    ]

    for method_name, processed_img in methods:
        print(f"\n🔧 Метод: {method_name}")

        for i, ocr_config in enumerate(configs):
            try:
                if len(processed_img.shape) == 3:  # Цветное изображение
                    pil_img = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
                else:  # Ч/Б изображение
                    pil_img = Image.fromarray(processed_img)

                text = pytesseract.image_to_string(pil_img, config=ocr_config, lang='eng')
                text_clean = text.strip()

                if text_clean:
                    print(f"   PSM {ocr_config[-1]}: '{text_clean}'")
                else:
                    print(f"   PSM {ocr_config[-1]}: (пусто)")

            except Exception as e:
                print(f"   PSM {ocr_config[-1]}: Ошибка - {e}")


def enhance_contrast(img):
    """Увеличивает контраст"""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)


def apply_threshold(img):
    """Применяет бинаризацию"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


if __name__ == "__main__":
    debug_ocr()
