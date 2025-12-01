import os
import shutil
import subprocess


def build_exe():
    """Функция сборки exe файла"""

    # Очистка предыдущих сборок
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # Команда PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',  # Один exe файл
        '--windowed',  # Без консоли (для GUI)
        '--name=PoE_Craft_Bot',  # Имя приложения
        '--icon=icon.ico',  # Иконка
        '--add-data=config.json;.',  # Включить конфиг
        '--clean',  # Очистка временных файлов
        '--noconfirm',  # Не спрашивать подтверждение

        # Скрытые импорты
        '--hidden-import=tkinter',
        '--hidden-import=pynput.keyboard',
        '--hidden-import=pynput.mouse',
        '--hidden-import=pyautogui',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=pytesseract',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=keyboard',

        'main_old.py'
    ]

    print("🚀 Начинаем сборку...")
    print("Команда:", ' '.join(cmd))

    try:
        # Запуск PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("✅ Сборка успешно завершена!")
            print(f"📁 Файл создан: dist/PoE_Craft_Bot.exe")

            # Копируем дополнительные файлы в dist
            if os.path.exists('config.json'):
                shutil.copy2('config.json', 'dist/config.json')
                print("📄 Конфиг скопирован в dist/")

        else:
            print("❌ Ошибка сборки!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")


if __name__ == "__main__":
    build_exe()
