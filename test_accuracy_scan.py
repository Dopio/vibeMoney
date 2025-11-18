import sys
import os
import json

from core.scanner import ItemScanner

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_accuracy_scan():
    """Тестирует поиск модов accuracy"""
    print("🎯 ТЕСТ ПОИСКА ACCURACY МОДОВ")
    print("=" * 50)

    # Загружаем конфиг
    with open('config.json', 'r') as f:
        config = json.load(f)

    scanner = ItemScanner()
    target_mods = config.get('target_mods', [])
    scan_region = config.get('scan_region')

    print(f"🔍 Целевые моды: {target_mods}")
    print(f"📐 Область сканирования: {scan_region}")

    if not scan_region:
        print("❌ Область сканирования не настроена!")
        return

    input("\n📷 Убедитесь что предмет с модами виден, затем нажмите Enter...")

    # Тестируем сканирование
    print("\n🔄 Сканирую...")
    mods = scanner.scan_item(scan_region)

    if mods:
        print(f"✅ Найдено модов: {len(mods)}")
        for i, mod in enumerate(mods, 1):
            print(f"   {i}. {mod}")

        # Проверяем есть ли целевые моды
        found_target = scanner.has_desired_mod(mods, target_mods)
        if found_target:
            print("🎉 ЦЕЛЕВОЙ МОД ACCURACY НАЙДЕН!")
        else:
            print("❌ Целевые моды accuracy не найдены")
    else:
        print("❌ Не удалось распознать моды")


if __name__ == "__main__":
    test_accuracy_scan()
