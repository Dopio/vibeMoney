import sys
import os

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui.main_window import main

    print("🚀 Запуск PoE Craft Bot GUI...")
    main()
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("📦 Устанавливаем зависимости...")

    # Авто-установка tkinter если нужно
    try:
        import tkinter

        print("✅ Tkinter установлен")
    except ImportError:
        print("❌ Tkinter не установлен. Установите: sudo apt-get install python3-tk (Linux)")

    input("Нажмите Enter для выхода...")
