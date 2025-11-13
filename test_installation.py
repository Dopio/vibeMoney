try:
    from PIL import ImageGrab, Image

    print("✅ Pillow установлен корректно")

    import pyautogui

    print("✅ PyAutoGUI установлен корректно")

    import pynput

    print("✅ pynput установлен корректно")

    import cv2

    print("✅ OpenCV установлен корректно")

    import pytesseract

    print("✅ pytesseract установлен корректно")

    # Тест захвата экрана
    screenshot = ImageGrab.grab()
    print(f"✅ Захват экрана работает. Размер: {screenshot.size}")

    # Тест позиции мыши
    x, y = pyautogui.position()
    print(f"✅ Мышь работает. Текущая позиция: ({x}, {y})")

    print("\n🎉 Все библиотеки установлены правильно!")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
except Exception as e:
    print(f"⚠️ Другая ошибка: {e}")