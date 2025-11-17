import os
import sys


def check_project_structure():
    print("🔍 ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА")
    print("=" * 50)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Текущая директория: {current_dir}")

    # Проверяем ключевые файлы
    files_to_check = [
        'run_gui.py',
        'gui/main_window.py',
        'gui/calibration_window.py',
        'config.json'
    ]

    for file_path in files_to_check:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} - найден")
        else:
            print(f"❌ {file_path} - не найден")

    # Проверяем импорты
    print("\n🔧 ПРОВЕРКА ИМПОРТОВ:")
    sys.path.append(current_dir)

    try:
        from gui.main_window import PoeCraftBotGUI
        print("✅ PoeCraftBotGUI импортируется")
    except Exception as e:
        print(f"❌ Ошибка импорта PoeCraftBotGUI: {e}")

    try:
        from gui.calibration_window import CalibrationWindow
        print("✅ CalibrationWindow импортируется")
    except Exception as e:
        print(f"❌ Ошибка импорта CalibrationWindow: {e}")


if __name__ == "__main__":
    check_project_structure()