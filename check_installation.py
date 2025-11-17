def check_dependencies():
    packages = [
        'cv2', 'pytesseract', 'PIL', 'pyautogui',
        'numpy', 'pynput', 'keyboard', 'matplotlib', 'pandas'
    ]

    print("=== Проверка зависимостей ===")
    print("=" * 40)

    all_good = True

    for package in packages:
        try:
            if package == 'PIL':
                __import__('PIL.Image')
                version = "OK"
            elif package == 'cv2':
                import cv2
                version = cv2.__version__
            elif package == 'numpy':
                import numpy
                version = numpy.__version__
            else:
                mod = __import__(package)
                version = getattr(mod, '__version__', 'OK')

            print(f"[OK] {package:15} - Установлен (v{version})")

        except ImportError as e:
            print(f"[ERROR] {package:15} - Ошибка: {e}")
            all_good = False
        except Exception as e:
            print(f"[WARN] {package:15} - Предупреждение: {e}")

    print("=" * 40)
    if all_good:
        print("Все зависимости работают корректно!")
    else:
        print("Есть проблемы с некоторыми зависимостями")


if __name__ == "__main__":
    check_dependencies()
