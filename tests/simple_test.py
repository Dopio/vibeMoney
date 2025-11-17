import os

print("=== ПРОСТОЙ ТЕСТ СИСТЕМЫ ===")
print("=" * 30)

# Проверяем основные модули
modules = ['cv2', 'numpy', 'pyautogui', 'PIL']

for module in modules:
    try:
        __import__(module)
        print(f"[OK] {module} - работает")
    except ImportError as e:
        print(f"[ERROR] {module} - ошибка: {e}")

# Проверяем структуру проекта
folders = ['config', 'core', 'gui', 'tests', 'utils']
print("\n=== ПРОВЕРКА СТРУКТУРЫ ===")
for folder in folders:
    if os.path.exists(folder):
        print(f"[OK] Папка {folder} - существует")
    else:
        print(f"[MISSING] Папка {folder} - отсутствует")

print("\n=== ГОТОВО ===")
