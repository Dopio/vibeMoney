from typing import Dict

import pyautogui
import time
import json
from pynput import keyboard
from pynput.mouse import Listener as MouseListener


class Calibrator:
    def __init__(self):
        self.positions: Dict[str, any] = {
            'currency': None,  # Orb of Alteration
            'item': None,  # Предмет для крафта
            'scan_region': None  # Область текста модов
        }
        self.current_step = 0
        self.calibration_steps = [
            "Наведите курсор на Orb of Alteration и нажмите F1",
            "Наведите курсор на предмет для крафта и нажмите F2",
            "Наведите курсор в ЛЕВЫЙ ВЕРХНИЙ угол области текста модов и нажмите F3",
            "Наведите курсор в ПРАВЫЙ НИЖНИЙ угол области текса модов и нажмите F4"
        ]

    def start_calibration(self):
        """Запуск процесса калибровки"""
        print("Запуск калибровки PoE Craft Bot")

        # Запускаем слушатели клавиатуры и мыши
        keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        mouse_listener = MouseListener(on_move=self.on_mouse_move)

        keyboard_listener.start()
        mouse_listener.start()

        # Ждем завершения калибровки
        while self.current_step < len(self.calibration_steps):
            time.sleep(0.1)

        keyboard_listener.stop()
        mouse_listener.stop()

        self.save_calibration()

    def on_mouse_move(self, x, y):
        """Отслеживаем движение мыши для отображения координат"""
        if self.current_step < len(self.calibration_steps):
            print(f"\r Текущие координаты: ({x}, {y})", end="", flush=True)

    def on_key_press(self, key):
        """Обработка нажатий клавиш"""
        try:
            if hasattr(key, 'char'):
                return

            if key == keyboard.Key.f1 and self.current_step == 0:
                self.positions['currency'] = pyautogui.position()
                print(f"\n✅ Orb of Alteration: {self.positions['currency']}")
                self.current_step += 1

            elif key == keyboard.Key.f2 and self.current_step == 1:
                self.positions['item'] = pyautogui.position()
                print(f"✅ Предмет: {self.positions['item']}")
                self.current_step += 1

            elif key == keyboard.Key.f3 and self.current_step == 2:
                self.positions['scan_region'] = [pyautogui.position(), None]
                print(f"✅ Левый верхний угол: {self.positions['scan_region'][0]}")
                self.current_step += 1

            elif key == keyboard.Key.f4 and self.current_step == 3:
                if self.positions['scan_region'][0]:
                    self.positions['scan_region'][1] = pyautogui.position()

                    # Преобразуем в формат (x, y, width, height)
                    x1, y1 = self.positions['scan_region'][0]
                    x2, y2 = self.positions['scan_region'][1]
                    self.positions['scan_region'] = (
                        min(x1, x2), min(y1, y2),
                        abs(x2 - x1), abs(y2 - y1)
                    )
                    print(f"✅ Область сканирования: {self.positions['scan_region']}")
                    self.current_step += 1

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

    def save_calibration(self):
        """Сохраняет калибровку в конфиг"""
        config = {
            'currency_position': self.positions['currency'],
            'item_position': self.positions['item'],
            'scan_region': self.positions['scan_region'],
            'target_mods': ["increased", "added", "support", "critical", "damage"]
        }

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        print("💾 Конфигурация сохранена в config.json")


def main():
    """Главная функция запуска калибровки"""

    calibrator = Calibrator()
    calibrator.start_calibration()


if __name__ == "__main__":
    main()
