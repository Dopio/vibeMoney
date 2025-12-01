import tkinter as tk
import os
import sys
import json


def resource_path(relative_path):
    """Получает правильный путь для ресурсов в exe и при разработке"""
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception as e:
        base_path = os.path.abspath(".")
        print(f'Error: {e}')

    return os.path.join(base_path, relative_path)


class Recraft:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PoE Craft Bot")
        self.root.geometry("800x600")

        # Загрузка конфига через resource_path
        config_path = resource_path('config.json')
        self.load_config(config_path)

        self.setup_ui()

    def load_config(self, config_path):
        """Загрузка конфигурации"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
                print("⚠️ Конфиг не найден, создан пустой")
        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            self.config = {}

    def setup_ui(self):
        """Настройка интерфейса"""
        # Ваш код GUI здесь
        label = tk.Label(self.root, text="PoE Craft Bot", font=("Arial", 16))
        label.pack(pady=20)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = Recraft()
    app.run()
