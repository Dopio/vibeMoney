import mss
from PIL import Image
import pytesseract


def test_mss_capture():
    print("🎯 ТЕСТ ЗАХВАТА ВТОРОГО МОНИТОРА С MSS")
    print("=" * 50)

    with mss.mss() as sct:
        # Получаем список всех мониторов
        print("🖥️ Доступные мониторы:")
        for i, monitor in enumerate(sct.monitors):
            print(f"   Монитор {i}: {monitor}")

        # Монитор 0 - все мониторы вместе, 1 - основной, 2 - второй и т.д.
        second_monitor = sct.monitors[2] if len(sct.monitors) > 2 else sct.monitors[1]
        print(f"\n🎯 Использую монитор: {second_monitor}")

        # Захватываем весь второй монитор
        screenshot = sct.grab(second_monitor)

        # Конвертируем в PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save('second_monitor_full.png')
        print("✅ Полный скриншот второго монитора: second_monitor_full.png")

        # Теперь тестируем вашу область на втором мониторе
        # Нужно пересчитать координаты относительно второго монитора
        monitor_left = second_monitor['left']
        monitor_top = second_monitor['top']

        # Ваши координаты из конфига
        region = [2328, 493, 285, 65]  # Абсолютные координаты
        x_abs, y_abs, w, h = region

        # Пересчитываем в относительные координаты второго монитора
        x_rel = x_abs - monitor_left
        y_rel = y_abs - monitor_top

        print(f"\n📐 Пересчет координат:")
        print(f"   Абсолютные: ({x_abs}, {y_abs})")
        print(f"   Относительные: ({x_rel}, {y_rel})")
        print(f"   Монитор: left={monitor_left}, top={monitor_top}")

        if 0 <= x_rel <= second_monitor['width'] and 0 <= y_rel <= second_monitor['height']:
            # Захватываем конкретную область на втором мониторе
            region_monitor = {
                'left': x_abs,
                'top': y_abs,
                'width': w,
                'height': h
            }

            region_screenshot = sct.grab(region_monitor)
            region_img = Image.frombytes("RGB", region_screenshot.size, region_screenshot.bgra, "raw", "BGRX")
            region_img.save('second_monitor_region.png')
            print("✅ Область на втором мониторе: second_monitor_region.png")

            # Пробуем распознать текст
            text = pytesseract.image_to_string(region_img, lang='eng')
            print(f"📝 Распознанный текст: '{text.strip()}'")

        else:
            print("❌ Координаты выходят за пределы второго монитора!")


if __name__ == "__main__":
    test_mss_capture()
