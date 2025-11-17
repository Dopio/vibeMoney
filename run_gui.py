import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui.main_window import PoeCraftBotGUI
    import tkinter as tk

    print("🚀 Запуск PoE Craft Bot GUI...")

    # Создаем главное окно и приложение
    root = tk.Tk()
    app = PoeCraftBotGUI(root)
    root.mainloop()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("🔍 Детали ошибки:")

    # Диагностика
    try:
        from gui import main_window

        print("✅ main_window модуль найден")
    except ImportError as e2:
        print(f"❌ Не удалось импортировать main_window: {e2}")

    try:
        import tkinter

        print("✅ Tkinter доступен")
    except ImportError:
        print("❌ Tkinter не установлен. Установите: sudo apt-get install python3-tk (Linux)")

    input("Нажмите Enter для выхода...")