import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_real_components():
    print("🧪 ТЕСТ РЕАЛЬНЫХ КОМПОНЕНТОВ")
    print("=" * 50)

    try:
        from core.controller import CraftController
        from core.scanner import ItemScanner
        from core.safety import SafetyManager

        safety = SafetyManager()
        controller = CraftController(safety)
        scanner = ItemScanner(safety)

        print("✅ Все компоненты импортируются")
        print(f"   Контроллер: {controller}")
        print(f"   Сканер: {scanner}")
        print(f"   Безопасность: {safety}")

        # Проверяем методы
        print("\n🔧 Проверка методов:")
        print(f"   Контроллер.use_currency: {'use_currency' in dir(controller)}")
        print(f"   Сканер.scan_item: {'scan_item' in dir(scanner)}")
        print(f"   Безопасность.check_all_safety_conditions: {'check_all_safety_conditions' in dir(safety)}")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    test_real_components()
