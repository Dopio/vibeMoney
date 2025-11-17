import json

# Ваши новые координаты из калибровки
new_config = {
    "currency_position": [2106, 368],
    "item_position": [2331, 446],
    "scan_region": [2134, 296, 400, 54],  # width: 2534-2134=400, height: 350-296=54
    "target_mods": ["increased", "damage", "critical", "speed"],
    "max_attempts": 200,
    "min_delay": 0.5,
    "max_delay": 2.0
}

# Принудительно сохраняем
with open('config.json', 'w') as f:
    json.dump(new_config, f, indent=4)

print("✅ Конфиг принудительно обновлен!")
print("Новые настройки:")
print(f"  Валюты: {new_config['currency_position']}")
print(f"  Предмет: {new_config['item_position']}")
print(f"  Область: {new_config['scan_region']}")
