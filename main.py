import json
import os
import time
import signal
import sys
import argparse
from config.settings import ConfigManager
from core.scanner import ItemScanner
from core.controller import CraftController
from core.safety import SafetyManager
from core.analyzer import CraftAnalyzer
from utils.calibrator import Calibrator
from utils.logger import CraftLogger


class PoeCraftBot:
    def __init__(self):
        self.config = None
        self.config_manager = ConfigManager()
        self.scanner = ItemScanner()
        self.controller = CraftController()
        self.safety = SafetyManager()
        self.analyzer = CraftAnalyzer()
        self.logger = CraftLogger()
        self.running = False

    def initialize(self):
        """Инициализация бота"""
        print("🔄 Инициализация PoE Craft Bot...")

        # ЗАГРУЖАЕМ КОНФИГ ПРЯМО ИЗ ФАЙЛА
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.config = json.load(f)
                print("✅ Конфиг загружен из config.json")
                print(f"   Валюты: {self.config.get('currency_position')}")
                print(f"   Предмет: {self.config.get('item_position')}")
                print(f"   Область: {self.config.get('scan_region')}")
            else:
                print("❌ config.json не найден! Запустите калибровку.")
                return False

        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            return False

        # Проверяем наличие калибровки
        if not self.config.get('currency_position'):
            print("❌ Требуется калибровка! Запустите calibrate.py")
            return False

        print("✅ Бот инициализирован")
        return True

    def start_crafting(self):
        """Запуск автоматического крафта"""
        if not self.initialize():
            return

        self.running = True
        print("🎮 Запуск крафта... Нажмите Ctrl+C для остановки")

        attempt = 0
        try:
            while self.running and attempt < self.config.max_attempts:
                attempt += 1
                self.craft_cycle(attempt)

        except KeyboardInterrupt:
            print("\n🛑 Остановлено пользователем")
        finally:
            self.shutdown()

    def craft_cycle(self, attempt):
        """Один цикл крафта"""
        print(f"♻️ Попытка {attempt}")

        # Используем Orb of Alteration
        self.controller.use_currency(
            self.config.currency_position,
            self.config.item_position
        )

        # Периодически проверяем результат
        if attempt % 3 == 0:  # Проверяем каждые 3 попытки
            self.check_item_mods(attempt)

    def check_item_mods(self, attempt):
        """Проверяем моды предмета"""
        mods = self.scanner.scan_item(self.config.scan_region)

        if mods and self.scanner.has_desired_mod(mods, self.config.target_mods):
            print(f"🎉 НУЖНЫЙ МОД НАЙДЕН! Попытка: {attempt}")
            self.running = False
        else:
            print(f"📄 Моды: {mods[:2] if mods else 'Не распознано'}...")

    def shutdown(self):
        """Корректное завершение"""
        print("🔴 Бот остановлен")


def signal_handler(sig, frame):
    print('\n🛑 Получен сигнал остановки')
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    bot = PoeCraftBot()
    bot.start_crafting()
