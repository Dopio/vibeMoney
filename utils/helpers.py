import pyautogui
import random
import time
import math


def human_delay(min_seconds=0.1, max_seconds=2.0):
    """Случайная задержка между действиями"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def human_curve_move(x, y, duration=0.5, curves=2):
    """Двигает мышью по ЕСТЕСТВЕННОЙ кривой траектории"""
    start_x, start_y = pyautogui.position()

    # Рассчитываем направление и расстояние
    dx = x - start_x
    dy = y - start_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Нормализуем направление
    if distance > 0:
        dir_x = dx / distance
        dir_y = dy / distance
    else:
        return

    # Создаем контрольные точки для плавной кривой
    control_points = [(start_x, start_y)]

    # Добавляем промежуточные точки с небольшими отклонениями
    for i in range(1, curves + 1):
        progress = i / (curves + 1)

        # Базовая точка на прямой линии
        base_x = start_x + dx * progress
        base_y = start_y + dy * progress

        # Небольшое отклонение перпендикулярно направлению (5-15% от расстояния)
        deviation_scale = random.uniform(0.05, 0.15)
        deviation = distance * deviation_scale

        # Перпендикулярное направление (90 градусов)
        perp_x = -dir_y
        perp_y = dir_x

        # Случайное отклонение влево или вправо
        if random.choice([True, False]):
            offset_x = perp_x * deviation
            offset_y = perp_y * deviation
        else:
            offset_x = -perp_x * deviation
            offset_y = -perp_y * deviation

        control_points.append((base_x + offset_x, base_y + offset_y))

    # Конечная точка
    control_points.append((x, y))

    # Анимация по кривой
    steps = int(duration * 60)  # Меньше шагов для плавности
    for step in range(steps + 1):
        t = step / steps
        current_x, current_y = bezier_point(control_points, t)
        pyautogui.moveTo(current_x, current_y, _pause=False)
        time.sleep(duration / steps)


def bezier_point(points, t):
    """Вычисляет точку на кривой Безье"""
    while len(points) > 1:
        new_points = []
        for i in range(len(points) - 1):
            x = (1 - t) * points[i][0] + t * points[i + 1][0]
            y = (1 - t) * points[i][1] + t * points[i + 1][1]
            new_points.append((x, y))
        points = new_points
    return points[0]


def human_click_advanced(x, y, variance=10):
    """Улучшенный человеческий клик с ЕСТЕСТВЕННЫМ движением"""
    # Случайное смещение
    offset_x = random.randint(-variance, variance)
    offset_y = random.randint(-variance, variance)
    target_x, target_y = x + offset_x, y + offset_y

    # Случайная длительность движения (быстрее для естественности)
    move_duration = random.uniform(0.2, 0.5)

    # Двигаемся по ЕСТЕСТВЕННОЙ кривой (1-2 небольших изгиба)
    human_curve_move(target_x, target_y, move_duration, curves=random.randint(1, 2))

    # Легкое дрожание перед кликом (редко)
    if random.random() > 0.8:
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-2, 2)
        pyautogui.moveRel(jitter_x, jitter_y, duration=0.03)
        time.sleep(0.05)

    # Клик
    pyautogui.click()  # Простой клик вместо раздельного mouseDown/Up

    # Задержка после клика
    human_delay(0.05, 0.2)


def human_click(x, y, variance=10):
    """Простой человеческий клик (для совместимости)"""
    # Случайное смещение
    offset_x = random.randint(-variance, variance)
    offset_y = random.randint(-variance, variance)

    # Случайная скорость движения
    move_duration = random.uniform(0.1, 0.3)

    # Двигаемся к цели
    pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

    # Клик
    pyautogui.click()

    # Задержка после клика
    human_delay(0.1, 0.3)


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
