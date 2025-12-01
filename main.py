import sys
import os


def resource_path(relative_path):
    """Получает правильный путь к ресурсам в exe и при разработке"""
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Добавляем пути для импорта (только если не в exe)
if not getattr(sys, 'frozen', False):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui.main_window import MainWindow
    import tkinter as tk

    print("🚀 Запуск PoE Craft Bot GUI...")

    # Загружаем конфиг через resource_path
    config_path = resource_path('config.json')
    print(f"📁 Путь к конфигу: {config_path}")

    # Создаем главное окно и приложение
    root = tk.Tk()
    app = MainWindow(root)  # Используем новый класс
    root.mainloop()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("🔍 Детали ошибки:")

    # Диагностика
    print(f"Python path: {sys.path}")
    print(f"Current dir: {os.getcwd()}")

    input("Нажмите Enter для выхода...")