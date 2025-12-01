import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_basic_tests():
    print("=== БАЗОВЫЕ ТЕСТЫ ===")

    # Тест 1: Импорты
    try:
        from core.safety import SafetyManager
        print("[OK] SafetyManager импортируется")
    except Exception as e:
        print(f"[ERROR] SafetyManager: {e}")

    try:
        from core.controller import CraftController
        print("[OK] CraftController импортируется")
    except Exception as e:
        print(f"[ERROR] CraftController: {e}")

    try:
        from core.scanner import ItemScanner
        print("[OK] ItemScanner импортируется")
    except Exception as e:
        print(f"[ERROR] ItemScanner: {e}")


def main():
    print("=== УПРОЩЕННОЕ ТЕСТИРОВАНИЕ ===")
    print("=" * 40)

    run_basic_tests()

    print("\n=== СЛЕДУЮЩИЕ ШАГИ ===")
    print("1. Установи Tesseract OCR")
    print("2. Запусти: python tests/test_safety.py")
    print("3. Запусти: python test_controller_scanner.py")
    print("4. Запусти GUI: python main.py")


if __name__ == "__main__":
    main()
