import sys
import os
from core.controller import CraftController
from core.scanner import ItemScanner
from core.safety import SafetyManager
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_controller():
    print("🎮 Тестирование контроллера...")

    safety = SafetyManager()
    controller = CraftController(safety)

    # Добавляем начальную задержку
    print("⏳ Начальная задержка...")
    time.sleep(1)

    # Тестовые координаты (замени на реальные после калибровки)
    test_currency_pos = (100, 100)
    test_item_pos = (200, 200)

    print("Тест 1: Одиночное действие")
    success = controller.use_currency(test_currency_pos, test_item_pos)
    print(f"Результат: {'✅ Успех' if success else '❌ Ошибка'}")

    print("\nТест 2: Несколько действий")
    for i in range(3):
        success = controller.use_currency(test_currency_pos, test_item_pos)
        print(f"Действие {i + 1}: {'✅' if success else '❌'}")
        time.sleep(1)


def test_scanner():
    print("\n🔍 Тестирование сканера...")

    safety = SafetyManager()
    scanner = ItemScanner(safety)

    # Тестовая область (замени на реальную после калибровки)
    test_region = (500, 500, 400, 300)

    print("Тест сканирования...")
    mods = scanner.scan_item(test_region)

    print(f"Найдено модов: {len(mods)}")
    for i, mod in enumerate(mods[:5]):  # Показываем первые 5
        print(f"  {i + 1}. {mod}")

    # Тест поиска целевых модов
    target_mods = ["increased", "damage", "critical"]
    has_desired = scanner.has_desired_mod(mods, target_mods)
    print(f"Найден целевой мод: {'✅ Да' if has_desired else '❌ Нет'}")


if __name__ == "__main__":
    test_controller()
    test_scanner()
