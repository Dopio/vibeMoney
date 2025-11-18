import pyautogui
from PIL import ImageGrab


def check_monitor_setup():
    print("🖥️ ПРОВЕРКА НАСТРОЙКИ МОНИТОРОВ")
    print("=" * 50)

    # Размер виртуального рабочего стола (всех мониторов)
    virtual_width, virtual_height = pyautogui.size()
    print(f"📏 Виртуальный рабочий стол: {virtual_width}x{virtual_height}")

    # Текущая позиция мыши
    mouse_x, mouse_y = pyautogui.position()
    print(f"📍 Мышь: ({mouse_x}, {mouse_y})")

    # Захватываем разные области для проверки
    regions_to_test = [
        (0, 0, 300, 300),  # Левый верх основного монитора
        (1920, 0, 300, 300),  # Левый верх второго монитора (если 1920x1080 основной)
        (2328, 493, 285, 65),  # Ваша текущая область
    ]

    for i, region in enumerate(regions_to_test):
        x, y, w, h = region
        try:
            screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            screenshot.save(f'monitor_test_{i}.png')
            print(f"✅ Область {region} -> monitor_test_{i}.png")
        except Exception as e:
            print(f"❌ Не удалось захватить {region}: {e}")


if __name__ == "__main__":
    check_monitor_setup()
