import sys
import os
from core.scanner import ItemScanner
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_right_monitor_scanner():
    print("🎯 ТЕСТ СКАНЕРА НА ПРАВОМ МОНИТОРЕ")
    print("=" * 50)

    # Загружаем конфиг
    with open('config.json', 'r') as f:
        config = json.load(f)

    scanner = ItemScanner()
    target_mods = config.get('target_mods', ['accuracy'])
    scan_region = config.get('scan_region', [2328, 493, 285, 65])

    print(f"🔍 Целевые моды: {target_mods}")
    print(f"📐 Область сканирования: {scan_region}")

    input("\n📷 Убедитесь что PoE на правом мониторе и нажмите Enter...")

    # Тестируем сканирование
    print("\n🔄 Сканирую на правом мониторе...")
    mods = scanner.scan_item(scan_region)

    if mods:
        print(f"✅ Найдено модов: {len(mods)}")
        for i, mod in enumerate(mods, 1):
            print(f"   {i}. {mod}")

        # Проверяем есть ли целевые моды
        found_target = scanner.has_desired_mod(mods, target_mods)
        if found_target:
            print("🎉 ЦЕЛЕВОЙ МОД НАЙДЕН НА ПРАВОМ МОНИТОРЕ!")
        else:
            print("❌ Целевые моды не найдены")
    else:
        print("❌ Не удалось распознать моды")


if __name__ == "__main__":
    test_right_monitor_scanner()
