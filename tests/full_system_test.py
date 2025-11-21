import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scanner import ItemScanner
from core.controller import CraftController
from core.safety import SafetyManager
import json


def full_system_test():
    print("🎯 ПОЛНЫЙ ТЕСТ СИСТЕМЫ С ПРАВЫМ МОНИТОРОМ")
    print("=" * 50)

    # Загружаем конфиг
    with open('../config.json', 'r') as f:
        config = json.load(f)

    print("📋 Конфигурация:")
    print(f"   Валюты: {config.get('currency_position')}")
    print(f"   Предмет: {config.get('item_position')}")
    print(f"   Область: {config.get('scan_region')}")
    print(f"   Целевые моды: {config.get('target_mods')}")

    # Инициализируем компоненты
    safety = SafetyManager()
    scanner = ItemScanner(safety)
    controller = CraftController(safety)

    input("\n🎮 Убедитесь что PoE на правом мониторе и нажмите Enter для теста...")

    # Тест 1: Сканирование
    print("\n1. 🔍 ТЕСТ СКАНЕРА:")
    mods = scanner.scan_item(config['scan_region'])

    if mods:
        print(f"   ✅ Найдено модов: {len(mods)}")
        for mod in mods:
            print(f"      - {mod}")

        # Проверяем целевые моды
        found = scanner.has_desired_mod(mods, config['target_mods'])
        if found:
            print("   🎉 ЦЕЛЕВОЙ МОД НАЙДЕН!")
        else:
            print("   ❌ Целевые моды не найдены")
    else:
        print("   ❌ Моды не распознаны")

    # Тест 2: Контроллер (опционально)
    test_controller = input("\n2. 🖱️ Протестировать контроллер? (y/n): ").lower().strip()
    if test_controller == 'y':
        print("   🔄 Тестирую использование валюты...")
        success = controller.use_currency(
            config['currency_position'],
            config['item_position']
        )
        if success:
            print("   ✅ Контроллер работает")
        else:
            print("   ❌ Ошибка контроллера")

    print("\n🏁 Тест завершен!")
    print("📝 Если все тесты пройдены - система готова к работе!")


if __name__ == "__main__":
    full_system_test()
