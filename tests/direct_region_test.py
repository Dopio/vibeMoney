import pyautogui
from PIL import ImageGrab, Image
import pytesseract
import json


def direct_region_test():
    print("🎯 ПРЯМАЯ ПРОВЕРКА ОБЛАСТИ (БЕЗ ОГРАНИЧЕНИЙ)")
    print("=" * 50)

    # Загружаем текущую область из конфига
    with open('../config.json', 'r') as f:
        config = json.load(f)

    region = config.get('scan_region', [2328, 493, 285, 65])
    x, y, w, h = region

    print(f"📐 Использую область из конфига: {region}")
    print(f"📍 Абсолютные координаты: ({x}, {y}) -> ({x + w}, {y + h})")

    input("📷 Убедитесь что PoE открыт на втором мониторе и нажмите Enter...")

    try:
        # Прямой захват без проверок
        print("\n📸 Захватываю область напрямую...")
        screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))

        # Сохраняем оригинал
        screenshot.save('direct_original.png')
        print("✅ Оригинальный скриншот: direct_original.png")

        # Показываем информацию о изображении
        print(f"📊 Размер изображения: {screenshot.size}")
        print(f"🎨 Режим: {screenshot.mode}")

        # Проверяем не пустое ли изображение
        if screenshot.getbbox() is None:
            print("❌ Изображение полностью пустое/черное!")
            return

        # Пробуем распознать текст
        print("\n🔍 Пробую распознать текст...")

        # Метод 1: Простое распознавание
        text_simple = pytesseract.image_to_string(screenshot, lang='eng')
        print(f"📝 Простое распознавание: '{text_simple.strip()}'")

        # Метод 2: С обработкой
        import cv2
        import numpy as np

        # Конвертируем в OpenCV
        img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Делаем черно-белым
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Увеличиваем контраст
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)

        # Сохраняем обработанное
        Image.fromarray(contrast).save('../direct_processed.png')
        print("✅ Обработанное изображение: direct_processed.png")

        # Распознаем обработанное
        text_processed = pytesseract.image_to_string(Image.fromarray(contrast), lang='eng')
        print(f"📝 После обработки: '{text_processed.strip()}'")

        # Ищем accuracy в любом виде
        all_text = (text_simple + " " + text_processed).lower()
        if "accuracy" in all_text:
            print("🎉 Слово 'accuracy' найдено в тексте!")
        else:
            print("❌ Слово 'accuracy' не найдено")

        # Показываем все уникальные слова
        words = set(word for word in all_text.split() if len(word) > 2)
        print(f"📖 Все найденные слова: {words}")

    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        print("Вероятно, область выходит за пределы доступного экрана")


if __name__ == "__main__":
    direct_region_test()
