import mss
from PIL import Image
import pytesseract


def find_right_monitor():
    print("🖥️ ПОИСК ПРАВОГО МОНИТОРА")
    print("=" * 50)

    with mss.mss() as sct:
        print("📋 Доступные мониторы:")
        monitors = sct.monitors

        for i, monitor in enumerate(monitors):
            print(f"\nМонитор {i}:")
            print(f"   Left: {monitor['left']}")
            print(f"   Top: {monitor['top']}")
            print(f"   Width: {monitor['width']}")
            print(f"   Height: {monitor['height']}")

            # Определяем положение монитора
            if i == 0:
                print("   📍 Виртуальный рабочий стол (все мониторы)")
            elif monitor['left'] == 0 and monitor['top'] == 0:
                print("   📍 Основной монитор (левый/верхний)")
            else:
                print("   📍 Дополнительный монитор")

        # Находим самый правый монитор
        rightmost_monitor = max(monitors[1:], key=lambda m: m['left'])
        print(f"\n🎯 Самый правый монитор:")
        print(f"   Index: {monitors.index(rightmost_monitor)}")
        print(f"   Position: left={rightmost_monitor['left']}, top={rightmost_monitor['top']}")
        print(f"   Size: {rightmost_monitor['width']}x{rightmost_monitor['height']}")

        return rightmost_monitor, monitors.index(rightmost_monitor)


def test_right_monitor(monitor, monitor_index):
    print(f"\n🧪 ТЕСТ ПРАВОГО МОНИТОРА #{monitor_index}")

    with mss.mss() as sct:
        # Захватываем весь правый монитор
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(f'right_monitor_full_{monitor_index}.png')
        print(f"✅ Полный скриншот правого монитора: right_monitor_full_{monitor_index}.png")

        # Тестируем область на правом мониторе
        # Ваши координаты из конфига
        region_abs = [2328, 493, 285, 65]  # Абсолютные координаты
        x_abs, y_abs, w, h = region_abs

        # Пересчитываем в относительные координаты правого монитора
        x_rel = x_abs - monitor['left']
        y_rel = y_abs - monitor['top']

        print(f"\n📐 Пересчет координат для правого монитора:")
        print(f"   Абсолютные: ({x_abs}, {y_abs})")
        print(f"   Относительные: ({x_rel}, {y_rel})")
        print(f"   Смещение монитора: left={monitor['left']}, top={monitor['top']}")

        if 0 <= x_rel <= monitor['width'] and 0 <= y_rel <= monitor['height']:
            # Захватываем область на правом мониторе
            region_monitor = {
                'left': x_abs,
                'top': y_abs,
                'width': w,
                'height': h
            }

            region_screenshot = sct.grab(region_monitor)
            region_img = Image.frombytes("RGB", region_screenshot.size, region_screenshot.bgra, "raw", "BGRX")
            region_img.save('right_monitor_region.png')
            print("✅ Область на правом мониторе: right_monitor_region.png")

            # Пробуем распознать текст
            text = pytesseract.image_to_string(region_img, lang='eng')
            print(f"📝 Распознанный текст: '{text.strip()}'")

            if 'accuracy' in text.lower():
                print("🎉 Accuracy найден на правом мониторе!")
            else:
                print("❌ Accuracy не найден")

        else:
            print("❌ Координаты выходят за пределы правого монитора!")


if __name__ == "__main__":
    right_monitor, monitor_index = find_right_monitor()
    test_right_monitor(right_monitor, monitor_index)
