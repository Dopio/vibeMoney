import random
import time
import pyautogui


def human_delay(min_seconds=0.1, max_seconds=2.0):
    """Случайная задержка между действиями"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def human_click(x, y, variance=10):
    """Клик с человеческой неточностью"""
    # Случайное смещение
    offset_x = random.randint(-variance, variance)
    offset_y = random.randint(-variance, variance)

    # Случайная скорость движения
    move_duration = random.uniform(0.1, 0.5)

    # Двигаемся к цели
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

    # Случайная длительность клика
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.05, 0.2))
    pyautogui.mouseUp()

    # Задержка после клика
    human_delay(0.1, 0.5)


def get_screen_center():
    """Возвращает центр экрана"""
    screen_width, screen_height = pyautogui.size()
    return screen_width // 2, screen_height // 2


def show_message(message):
    """Показывает сообщение в консоли с временной меткой"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def setup_tesseract():
    """Автоматически настраивает путь к Tesseract"""
    import pytesseract
    import os

    # Возможные пути установки
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract найден: {path}")
            return True

    print("❌ Tesseract не найден. Установи с: https://github.com/UB-Mannheim/tesseract/wiki")
    return False
