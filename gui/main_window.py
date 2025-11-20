import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Импортируем наши компоненты
from .components import MainTab, LogDisplay
from .components.tabs.settings_tab import SettingsTab
from .components.tabs.stats_tab import StatsTab


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Craft Bot v2.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Состояние бота
        self.bot_running = False
        self.bot_thread = None
        self.current_config = None
        self.bot = None

        # Компоненты интерфейса
        self.main_tab = None
        self.settings_tab = None
        self.stats_tab = None
        self.log_display = None

        # Создаем интерфейс
        self.create_widgets()
        self.setup_layout()

        # Загружаем конфиг при запуске
        self.load_config()

    def create_widgets(self):
        """Создает все элементы интерфейса с использованием компонентов"""
        # Вкладки
        self.notebook = ttk.Notebook(self.root)

        # 🔧 ГЛАВНАЯ ВКЛАДКА
        self.main_tab = MainTab(
            self.notebook,
            start_callback=self.start_bot,
            stop_callback=self.stop_bot,
            calibrate_callback=self.start_calibration
        )
        self.notebook.add(self.main_tab, text="🎮 Главная")

        # 🔧 ВКЛАДКА НАСТРОЕК
        self.settings_tab = SettingsTab(
            self.notebook,
            save_callback=self.save_settings,
            load_callback=self.load_settings
        )
        self.notebook.add(self.settings_tab, text="⚙️ Настройки")

        # 🔧 ВКЛАДКА СТАТИСТИКИ
        self.stats_tab = StatsTab(
            self.notebook,
            update_callback=self.update_stats,
            export_callback=self.export_stats
        )
        self.notebook.add(self.stats_tab, text="📊 Статистика")

        # 🔧 ВКЛАДКА ЛОГОВ
        self.log_display = LogDisplay(
            self.notebook,
            clear_callback=self.clear_logs,
            save_callback=self.save_logs
        )
        self.notebook.add(self.log_display, text="📝 Логи")

    def setup_layout(self):
        """Настраивает layout интерфейса"""
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def load_config(self):
        """Загружает конфигурацию и обновляет GUI"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    self.current_config = json.load(f)
                self.log_message("✅ Конфиг загружен")
                return True
            else:
                self.log_message("❌ Конфиг не найден")
                self.current_config = {}  # Инициализируем пустым словарем
                return False

        except Exception as e:
            self.log_message(f"❌ Ошибка загрузки конфига: {e}")
            self.current_config = {}  # Инициализируем пустым словарем
            return False

    def update_gui_from_config(self):
        """Обновляет все компоненты GUI из загруженного конфига"""
        try:
            if self.current_config:
                # Обновляем главную вкладку
                info_text = self._generate_config_info()
                self.main_tab.update_info(info_text)

                # Обновляем вкладку настроек
                self.settings_tab.update_from_config(self.current_config)

                # Обновляем статистику
                self.update_stats()

            self.log_message("✅ GUI обновлен из конфига")

        except Exception as e:
            self.log_message(f"⚠️ Ошибка обновления GUI: {e}")

    def _generate_config_info(self):
        """Генерирует текст информации о конфиге"""
        if not self.current_config:
            return "❌ Конфиг не загружен. Требуется калибровка!"

        return f"""
🎯 Целевые моды: {', '.join(self.current_config.get('target_mods', []))}
💰 Позиция валюты: {self.current_config.get('currency_position', 'Не задана')}
🎒 Позиция предмета: {self.current_config.get('item_position', 'Не задана')}
📏 Область сканирования: {self.current_config.get('scan_region', 'Не задана')}
🔢 Максимум попыток: {self.current_config.get('max_attempts', 1000)}
🛡️ Безопасность: ВКЛЮЧЕНА
        """

    def start_bot(self):
        """Запускает бота в отдельном потоке"""
        if not self.bot_running:
            # Проверяем наличие конфига
            if not self._validate_config():
                return

            self.log_message("🔍 Проверка конфига...")
            self.log_message(f"   Валюты: {self.current_config.get('currency_position')}")
            self.log_message(f"   Предмет: {self.current_config.get('item_position')}")
            self.log_message(f"   Область: {self.current_config.get('scan_region')}")

            # Создаем экземпляр бота
            try:
                from core.bot import PoeCraftBot
                self.bot = PoeCraftBot()  # Создаем без параметров

                # Инициализируем бота с конфигом
                if not self.bot.initialize(self.current_config):
                    self.log_message("❌ Не удалось инициализировать бота")
                    return

            except ImportError as e:
                self.log_message(f"❌ Ошибка импорта бота: {e}")
                return
            except Exception as e:
                self.log_message(f"❌ Ошибка инициализации бота: {e}")
                return

            # Обновляем статус через компонент
            self.main_tab.set_running_state("Запуск бота...")

            # Запускаем бота
            self.bot_running = True
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

            self.log_message("🎮 Бот запущен - начинаем крафт!")

    def _validate_config(self):
        """Проверяет валидность конфига"""
        if not self.current_config:
            self.log_message("❌ Конфиг не загружен!")
            messagebox.showerror("Ошибка", "Конфиг не загружен!\nСначала выполните калибровку.")
            return False

        required_fields = ['currency_position', 'item_position', 'scan_region']
        missing_fields = [field for field in required_fields if not self.current_config.get(field)]

        if missing_fields:
            self.log_message(f"❌ Отсутствуют поля: {missing_fields}")
            messagebox.showerror("Ошибка",
                                 f"В конфиге отсутствуют поля: {', '.join(missing_fields)}\nВыполните калибровку заново.")
            return False

        self.log_message("✅ Конфиг валиден")
        return True

    def run_bot(self):
        """Основной цикл бота"""
        try:
            if self.bot and self.current_config:
                self.log_message("🎮 Запуск бота...")
                self.log_message("🎯 F12 для экстренной остановки")

                # Пауза для подготовки
                time.sleep(2)

                # Получаем настройки
                target_mods = self.current_config.get('target_mods', ['accuracy'])
                max_attempts = self.current_config.get('max_attempts', 200)

                self.log_message(f"🎯 Целевые моды: {', '.join(target_mods)}")
                self.log_message(f"🔢 Максимум попыток: {max_attempts}")

                # Обновляем прогресс
                self.main_tab.set_progress_text(f"Крафт... 0/{max_attempts}")

                # Запускаем крафт - передаем параметры в start_crafting
                success = self.bot.start_crafting(
                    max_attempts=max_attempts,
                    target_mods=target_mods
                )

                # Обработка результата
                if success:
                    self.log_message("🎉 КРАФТ УСПЕШЕН! Найден нужный мод!")
                else:
                    if self.bot.safety and self.bot.safety.check_emergency_stop_requested():
                        self.log_message("🚨 ОСТАНОВЛЕНО ПО F12")
                    else:
                        self.log_message("❌ Целевой мод не найден")

            else:
                self.log_message("❌ Ошибка: бот не инициализирован")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log_message(f"❌ Критическая ошибка: {e}")
            self.log_message(f"📋 Детали: {error_details}")

        finally:
            # Всегда останавливаем бота
            self.root.after(0, self.stop_bot)

    def stop_bot(self):
        """Останавливает бота"""
        self.bot_running = False

        # Останавливаем бота
        if self.bot:
            self.bot.stop_crafting()

        # Обновляем статус через компонент
        self.main_tab.set_stopped_state("Бот остановлен")

        self.log_message("🛑 Бот остановлен")
        self.update_stats()

    def start_calibration(self):
        """Запускает графическую калибровку"""
        try:
            from .calibration_window import CalibrationWindow
            cal_window = CalibrationWindow(self)
            self.root.wait_window(cal_window.window)

            # Перезагружаем конфиг после калибровки
            self.force_config_reload()
            self.update_gui_from_config()
            self.log_message("✅ Калибровка завершена - настройки обновлены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить калибровку: {e}")
            self.log_message(f"❌ Ошибка калибровки: {e}")

    def save_settings(self):
        """Сохраняет настройки из GUI в конфиг"""
        try:
            # Получаем настройки из компонента настроек
            settings_data = self.settings_tab.get_settings()

            # Обновляем текущий конфиг
            if self.current_config is None:
                self.current_config = {}

            self.current_config.update(settings_data)

            # Сохраняем в файл
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=4)

            messagebox.showinfo("Сохранение", "Настройки сохранены! ✅")
            self.log_message("💾 Настройки сохранены в config.json")

            # Обновляем GUI
            self.update_gui_from_config()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
            self.log_message(f"❌ Ошибка сохранения настроек: {e}")

    def load_settings(self):
        """Загружает настройки из файла"""
        if self.load_config():
            messagebox.showinfo("Загрузка", "Настройки загружены! ✅")
            self.log_message("🔄 Настройки загружены из config.json")
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить настройки!")

    def update_stats(self):
        """Обновляет статистику"""
        try:
            stats_text = "📊 Статистика появится после запуска бота..."

            if self.bot:
                stats = self.bot.get_stats()
                stats_text = self._generate_stats_text(stats)

            self.stats_tab.update_stats(stats_text)

        except Exception as e:
            self.log_message(f"⚠️ Ошибка обновления статистики: {e}")

    def _generate_stats_text(self, stats):
        """Генерирует текст статистики"""
        bot_stats = stats.get('bot', {})
        controller_stats = stats.get('controller', {})
        scanner_stats = stats.get('scanner', {})

        return f"""
🤖 СТАТИСТИКА БОТА:
├── Состояние: {'🟢 Запущен' if bot_stats.get('running') else '🛑 Остановлен'}
├── Конфиг: {'✅ Загружен' if bot_stats.get('config_loaded') else '❌ Отсутствует'}
└── Действий: {controller_stats.get('total_actions', 0)}

🎯 КОНТРОЛЛЕР:
├── Всего действий: {controller_stats.get('total_actions', 0)}
├── Shift: {'Зажат' if controller_stats.get('shift_held') else 'Отпущен'}
└── Статус: {controller_stats.get('status', 'unknown')}

🔍 СКАНЕР:
├── Всего сканирований: {scanner_stats.get('total_scans', 0)}
└── Статус: {scanner_stats.get('status', 'unknown')}
        """

    def export_stats(self):
        """Экспортирует статистику"""
        try:
            if self.bot:
                stats = self.bot.get_stats()
                with open('stats.json', 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Экспорт", "Статистика экспортирована в stats.json ✅")
                self.log_message("📊 Статистика экспортирована в stats.json")
            else:
                messagebox.showwarning("Экспорт", "Нет данных для экспорта")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать статистику: {e}")

    def clear_logs(self):
        """Очищает логи"""
        self.log_display.clear_logs()
        self.log_message("🧹 Логи очищены")

    def save_logs(self):
        """Сохраняет логи в файл"""
        try:
            self.log_display.save_logs()
            self.log_message("💾 Логи сохранены в craft_bot.log")
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения логов: {e}")

    def force_config_reload(self):
        """Принудительно перезагружает конфиг из файла"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    self.current_config = json.load(f)
                self.log_message("🔄 Конфиг перезагружен из файла")
                return True
            else:
                self.log_message("❌ config.json не найден")
                return False
        except Exception as e:
            self.log_message(f"❌ Ошибка перезагрузки конфига: {e}")
            return False

    def log_message(self, message):
        """Добавляет сообщение в логи через компонент"""
        self.log_display.add_message(message)
