import json
import os
from tkinter import ttk, messagebox
import threading
import time
from .components import MainTab, LogDisplay
from .components.tabs.settings_tab import SettingsTab
from .components.tabs.stats_tab import StatsTab
from .components.tabs.mass_craft_tab import MassCraftTab


class MainWindow:
    def __init__(self, root):
        self.save_to_config = None
        self.notebook = None
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

        # Новые компоненты для массового крафта
        self.mass_craft_tab = None

        # Создаем интерфейс
        self.create_widgets()
        self.setup_layout()

        # Загружаем конфиг при запуске
        self.load_config()
        self.update_gui_from_config()

    def create_widgets(self):
        """Создает все элементы интерфейса с использованием компонентов"""
        # Вкладки
        self.notebook = ttk.Notebook(self.root)

        # 🔧 ГЛАВНАЯ ВКЛАДКА
        self.main_tab = MainTab(
            self.notebook,
            start_callback=self.start_bot,
            stop_callback=self.stop_bot,
            calibrate_callback=self.start_calibration,
            calibrate_stash_callback=self.open_stash_calibration
        )
        self.notebook.add(self.main_tab, text="🎮 Главная")

        # 🔧 МАССОВЫЙ КРАФТ
        self.mass_craft_tab = MassCraftTab(
            self.notebook,
            start_callback=self.start_mass_craft,
            stop_callback=self.stop_mass_craft,
            config_callback=self.save_to_config
        )
        self.notebook.add(self.mass_craft_tab, text="🔄 Массовый крафт")

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

    def save_to_config(self, key, value):
        """Сохраняет значение в конфиг (callback для MassCraftTab)"""
        try:
            if self.current_config is None:
                self.current_config = {}

            self.current_config[key] = value

            # Автосохранение в файл
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=4)

            self.log_message(f"💾 Настройка '{key}' сохранена в конфиг")

        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения в конфиг: {e}")

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

                # Обновляем вкладку массового крафта
                item_slots = self.current_config.get('item_slots', [])
                self.mass_craft_tab.update_items_info(len(item_slots))

                # Загружаем целевые моды
                target_mods = self.current_config.get('target_mods', [])
                if target_mods and hasattr(self.mass_craft_tab, 'set_target_mods'):
                    self.mass_craft_tab.set_target_mods(target_mods)

                # Устанавливаем позицию вкладки если бот уже создан
                stash_tab_pos = self.current_config.get('stash_tab_position')
                if stash_tab_pos and self.bot and hasattr(self.bot.controller, 'set_stash_tab_position'):
                    self.bot.controller.set_stash_tab_position(stash_tab_pos)

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

        info = f"""
    🎯 Целевые моды: {', '.join(self.current_config.get('target_mods', []))}
    💰 Позиция валюты: {self.current_config.get('currency_position', 'Не задана')}
    🎒 Позиция предмета: {self.current_config.get('item_position', 'Не задана')}
    📏 Область сканирования: {self.current_config.get('scan_region', 'Не задана')}
    🔢 Максимум попыток: {self.current_config.get('max_attempts', 1000)}
    🛡️ Безопасность: ВКЛЮЧЕНА
        """

        if 'stash_tab_position' in self.current_config:
            item_slots_count = len(self.current_config.get('item_slots', []))
            info += f"""
    📦 ДАННЫЕ ВКЛАДКИ:
    ├── Позиция вкладки: {self.current_config.get('stash_tab_position')}
    ├── Область предметов: {self.current_config.get('item_area_region', 'Не задана')}
    └── Слотов предметов: {item_slots_count} {'✅' if item_slots_count > 0 else '❌'}
            """

        return info

    def start_mass_craft(self, target_mods, max_attempts_per_item):
        """Запускает массовый крафт"""
        if not self.bot_running:

            # СОХРАНЯЕМ целевые моды в конфиг при запуске
            # if target_mods:
                # self.save_to_config('target_mods', target_mods)

            # Проверяем и сбрасываем флаги безопасности перед запуском
            if self.bot and hasattr(self.bot, 'safety'):
                if self.bot.safety.emergency_stop_requested:
                    self.log_message("🔄 Сбрасываем флаги безопасности перед запуском...")
                    self.bot.safety.reset_emergency_stop()

            self.log_message("🔍 ДЕБАГ: Начало start_mass_craft")

            # Проверяем наличие конфига и слотов предметов
            if not self._validate_mass_craft_config():
                self.log_message("❌ ДЕБАГ: Не пройдена валидация конфига")
                return

            # Проверяем наличие слотов предметов
            item_slots = self.current_config.get('item_slots', [])
            self.log_message(f"🔍 ДЕБАГ: Найдено слотов предметов: {len(item_slots)}")

            if not item_slots:
                messagebox.showerror("Ошибка",
                                     "Нет калиброванных слотов предметов!\nСначала выполните калибровку вкладки.")
                return

            self.log_message(f"🚀 Запуск массового крафта для {len(item_slots)} предметов")
            self.log_message(f"🎯 Целевые моды: {', '.join(target_mods)}")
            self.log_message(f"🔢 Макс. попыток на предмет: {max_attempts_per_item}")

            # Создаем экземпляр бота если нужно
            if not self.bot:
                self.log_message("🔍 ДЕБАГ: Создаем экземпляр бота")
                from core.bot import PoeCraftBot
                self.bot = PoeCraftBot()
                if not self.bot.initialize(self.current_config):
                    self.log_message("❌ Не удалось инициализировать бота")
                    return
            else:
                self.log_message("🔍 ДЕБАГ: Бот уже создан")

            # Устанавливаем слоты предметов в контроллер
            if hasattr(self.bot, 'controller') and hasattr(self.bot.controller, 'set_item_slots'):
                self.log_message("🔍 ДЕБАГ: Устанавливаем слоты предметов в контроллер")
                self.bot.controller.set_item_slots(item_slots)
            else:
                self.log_message("❌ ДЕБАГ: Контроллер не имеет метода set_item_slots")

                # Устанавливаем позицию вкладки stash
            stash_tab_pos = self.current_config.get('stash_tab_position')
            if stash_tab_pos and hasattr(self.bot.controller, 'set_stash_tab_position'):
                self.log_message("🔍 ДЕБАГ: Устанавливаем позицию вкладки stash")
                self.bot.controller.set_stash_tab_position(stash_tab_pos)
            else:
                self.log_message("❌ ДЕБАГ: Не удалось установить позицию вкладки")

            # Обновляем интерфейс
            self.mass_craft_tab.set_running_state("Запуск массового крафта...")
            self.mass_craft_tab.update_items_info(len(item_slots))

            # Запускаем массовый крафт
            self.bot_running = True
            self.log_message("🔍 ДЕБАГ: Запускаем поток массового крафта")

            self.bot_thread = threading.Thread(
                target=self.run_mass_craft,
                args=(target_mods, max_attempts_per_item),
                daemon=True
            )
            self.bot_thread.start()

            # ЗАПУСКАЕМ ОБНОВЛЕНИЕ ПРОГРЕССА
            self.update_mass_craft_progress()

            self.log_message("✅ ДЕБАГ: Поток массового крафта запущен")
        else:
            self.log_message("⚠️ ДЕБАГ: Бот уже запущен")

    def run_mass_craft(self, target_mods, max_attempts_per_item):
        """Основной цикл массового крафта"""
        try:
            self.log_message("🔍 ДЕБАГ: Начало run_mass_craft")

            if self.bot and hasattr(self.bot, 'start_mass_craft'):
                self.log_message("🔍 ДЕБАГ: Бот поддерживает массовый крафт")

                # Получаем позицию валюты
                currency_pos = self.current_config.get('currency_position')
                self.log_message(f"🔍 ДЕБАГ: Позиция валюты: {currency_pos}")

                # Запускаем массовый крафт
                self.log_message("🔍 ДЕБАГ: Вызываем bot.start_mass_craft")
                success = self.bot.start_mass_craft(
                    currency_pos=currency_pos,
                    target_mods=target_mods,
                    max_attempts_per_item=max_attempts_per_item
                )

                self.log_message(f"🔍 ДЕБАГ: Результат start_mass_craft: {success}")

                # Обновляем интерфейс по завершении
                self.root.after(0, self._on_mass_craft_finished, success)

            else:
                self.log_message("❌ ДЕБАГ: Бот не поддерживает массовый крафт")
                if not self.bot:
                    self.log_message("❌ ДЕБАГ: Бот не инициализирован")
                else:
                    self.log_message(
                        f"❌ ДЕБАГ: У бота нет метода start_mass_craft: {hasattr(self.bot, 'start_mass_craft')}")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log_message(f"❌ Ошибка массового крафта: {e}")
            self.log_message(f"📋 Детали: {error_details}")
            self.root.after(0, self._on_mass_craft_finished, False)

    def _on_mass_craft_finished(self, success):
        """Обработка завершения массового крафта"""
        self.bot_running = False

        if success:
            self.mass_craft_tab.set_stopped_state("Массовый крафт завершен успешно!")
            self.log_message("🎉 Массовый крафт завершен успешно!")
        else:
            self.mass_craft_tab.set_stopped_state("Массовый крафт прерван")
            self.log_message("❌ Массовый крафт прерван")

        self.update_stats()

    def stop_mass_craft(self):
        """Останавливает массовый крафт и сбрасывает состояние"""
        self.log_message("🛑 Запрошена остановка массового крафта...")
        self.bot_running = False

        # Останавливаем массовый крафт в контроллере
        if self.bot and hasattr(self.bot.controller, 'stop_mass_craft'):
            self.bot.controller.stop_mass_craft()
            self.log_message("✅ Команда остановки передана контроллеру")

        # ПОЛНОСТЬЮ сбрасываем флаги безопасности
        if self.bot and hasattr(self.bot, 'safety'):
            self.bot.safety.reset_emergency_stop()  # NEW: используем новый метод
            self.log_message("🔄 Флаги безопасности сброшены")

        # Обновляем интерфейс
        self.mass_craft_tab.set_stopped_state("Массовый крафт остановлен")
        self.log_message("🛑 Массовый крафт остановлен")
        self.update_stats()

    def update_mass_craft_progress(self):
        """Обновляет прогресс массового крафта"""
        if self.bot_running and self.bot and hasattr(self.bot.controller, 'get_mass_craft_progress'):
            try:
                progress = self.bot.controller.get_mass_craft_progress()
                stats = self.bot.controller.get_stats()

                current_item = stats.get('current_item', 0) + 1
                total_items = max(stats.get('total_items', 1), 1)  # избегаем деления на 0

                self.mass_craft_tab.update_progress(progress, current_item, total_items)

                # Планируем следующее обновление
                if self.bot_running:
                    self.root.after(1000, self.update_mass_craft_progress)
            except Exception as e:
                self.log_message(f"⚠️ Ошибка обновления прогресса: {e}")

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
                                 f"В конфиге отсутствуют поля: "
                                 f"{', '.join(missing_fields)}\nВыполните калибровку заново.")
            return False

        self.log_message("✅ Конфиг валиден")
        return True

    def _validate_mass_craft_config(self):
        """Проверяет конфиг для массового крафта"""
        self.log_message("🔍 ДЕБАГ: Начало валидации конфига массового крафта")

        if not self.current_config:
            self.log_message("❌ Конфиг не загружен!")
            messagebox.showerror("Ошибка", "Конфиг не загружен!\nСначала выполните калибровку.")
            return False

        self.log_message(f"🔍 ДЕБАГ: Конфиг загружен, ключи: {list(self.current_config.keys())}")

        # Проверяем обязательные поля
        required_fields = ['currency_position', 'stash_tab_position']
        missing_fields = [field for field in required_fields if not self.current_config.get(field)]

        if missing_fields:
            self.log_message(f"❌ Отсутствуют поля: {missing_fields}")
            messagebox.showerror("Ошибка",
                                 f"В конфиге отсутствуют поля: "
                                 f"{', '.join(missing_fields)}\nВыполните калибровку заново.")
            return False

        # Проверяем наличие слотов предметов (не обязательно, но желательно)
        item_slots = self.current_config.get('item_slots', [])
        self.log_message(f"🔍 ДЕБАГ: item_slots: {len(item_slots)} слотов")

        if not item_slots:
            self.log_message("⚠️ ДЕБАГ: item_slots пуст - возможно, не выполнена калибровка вкладки")
            # Не блокируем запуск, но предупреждаем
            result = messagebox.askyesno(
                "Предупреждение",
                "Не найдены слоты предметов. Возможно, не выполнена калибровка вкладки.\nПродолжить?"
            )
            if not result:
                return False

        self.log_message("✅ ДЕБАГ: Валидация конфига массового крафта пройдена")
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
        """Останавливает бота и сбрасывает состояние"""
        self.bot_running = False

        # Останавливаем бота
        if self.bot:
            self.bot.stop_crafting()

        # Сбрасываем флаги безопасности
        if self.bot and hasattr(self.bot, 'safety'):
            self.bot.safety.reset_emergency_stop()  # NEW: используем новый метод

        # Обновляем статус через компонент
        self.main_tab.set_stopped_state("Бот остановлен")

        self.log_message("🛑 Бот остановлен")
        self.update_stats()

    def on_emergency_stop(self, event=None):
        """Обработчик F12 - использует существующую систему безопасности"""
        self.log_message("🚨 АКТИВИРОВАНА ЭКСТРЕННАЯ ОСТАНОВКА ПО F12!")

        # Просто устанавливаем флаг в SafetyManager - он уже обрабатывается
        if self.bot and hasattr(self.bot, 'safety'):
            self.bot.safety.emergency_stop_requested = True

        # Останавливаем интерфейс
        if self.bot_running:
            if hasattr(self, 'mass_craft_tab') and self.mass_craft_tab.stop_btn['state'] == 'normal':
                self.stop_mass_craft()
            else:
                self.stop_bot()
        else:
            self.log_message("ℹ️ Бот уже остановлен")

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

    def open_stash_calibration(self):
        """Открывает окно калибровки вкладки"""
        try:
            from .stash_calibration_window import StashCalibrationWindow
            stash_cal_window = StashCalibrationWindow(self)
            self.root.wait_window(stash_cal_window.window)

            # Перезагружаем конфиг после калибровки вкладки
            self.force_config_reload()
            self.update_gui_from_config()
            self.log_message("✅ Калибровка вкладки завершена - настройки обновлены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить калибровку вкладки: {e}")
            self.log_message(f"❌ Ошибка калибровки вкладки: {e}")

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

    @classmethod
    def _generate_stats_text(cls, stats):
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
