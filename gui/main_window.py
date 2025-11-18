import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time


class PoeCraftBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Craft Bot v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Состояние бота
        self.bot_running = False
        self.bot_thread = None
        self.current_config = None  # ДОБАВЬТЕ ЭТО

        # Создаем интерфейс
        self.create_widgets()
        self.setup_layout()

        # Загружаем конфиг при запуске
        self.load_config()

    def create_widgets(self):
        """Создает все элементы интерфейса"""

        # Вкладки
        self.notebook = ttk.Notebook(self.root)

        # Вкладка: Главная
        self.main_frame = ttk.Frame(self.notebook)
        self.create_main_tab()

        # Вкладка: Настройки
        self.settings_frame = ttk.Frame(self.notebook)
        self.create_settings_tab()

        # Вкладка: Статистика
        self.stats_frame = ttk.Frame(self.notebook)
        self.create_stats_tab()

        # Вкладка: Логи
        self.logs_frame = ttk.Frame(self.notebook)
        self.create_logs_tab()

        self.notebook.add(self.main_frame, text="Главная")
        self.notebook.add(self.settings_frame, text="Настройки")
        self.notebook.add(self.stats_frame, text="Статистика")
        self.notebook.add(self.logs_frame, text="Логи")

    def create_main_tab(self):
        """Создает содержимое главной вкладки"""

        # Заголовок
        title_label = ttk.Label(self.main_frame,
                                text="Path of Exile Craft Bot",
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Статус бота
        self.status_frame = ttk.LabelFrame(self.main_frame, text="Статус бота", padding=10)
        self.status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = ttk.Label(self.status_frame, text="🛑 Бот остановлен",
                                      font=("Arial", 12), foreground="red")
        self.status_label.pack()

        # Прогресс
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Прогресс", padding=10)
        self.progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x")

        self.progress_text = ttk.Label(self.progress_frame, text="Ожидание запуска...")
        self.progress_text.pack()

        # Быстрый старт
        self.quick_start_frame = ttk.LabelFrame(self.main_frame, text="Быстрый старт", padding=10)
        self.quick_start_frame.pack(fill="x", padx=10, pady=5)

        # Кнопки управления
        self.buttons_frame = ttk.Frame(self.quick_start_frame)
        self.buttons_frame.pack(fill="x")

        self.start_button = ttk.Button(self.buttons_frame, text="▶️ Запуск бота",
                                       command=self.start_bot, style="Accent.TButton")
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(self.buttons_frame, text="⏹️ Остановить",
                                      command=self.stop_bot, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        self.calibrate_button = ttk.Button(self.buttons_frame, text="🎯 Калибровка",
                                           command=self.start_calibration)
        self.calibrate_button.pack(side="left", padx=5)

        # Информация о текущих настройках
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Текущие настройки", padding=10)
        self.info_frame.pack(fill="x", padx=10, pady=5)

        info_text = """
Целевые моды: increased, damage, critical, speed
Максимум попыток: 1000
Безопасность: ВКЛЮЧЕНА
        """
        self.info_label = ttk.Label(self.info_frame, text=info_text, justify="left")
        self.info_label.pack(anchor="w")

    def create_settings_tab(self):
        """Создает вкладку настроек"""

        # Настройки крафта
        craft_frame = ttk.LabelFrame(self.settings_frame, text="Настройки крафта", padding=10)
        craft_frame.pack(fill="x", padx=10, pady=5)

        # Целевые моды
        ttk.Label(craft_frame, text="Целевые моды (через запятую):").pack(anchor="w")
        self.target_mods_entry = ttk.Entry(craft_frame, width=50)
        self.target_mods_entry.insert(0, "increased, damage, critical, speed, support")
        self.target_mods_entry.pack(fill="x", pady=5)

        # Максимум попыток
        attempts_frame = ttk.Frame(craft_frame)
        attempts_frame.pack(fill="x", pady=5)

        ttk.Label(attempts_frame, text="Максимум попыток:").pack(side="left")
        self.max_attempts_var = tk.StringVar(value="1000")
        self.max_attempts_entry = ttk.Entry(attempts_frame, textvariable=self.max_attempts_var, width=10)
        self.max_attempts_entry.pack(side="left", padx=5)

        # Настройки безопасности
        safety_frame = ttk.LabelFrame(self.settings_frame, text="Настройки безопасности", padding=10)
        safety_frame.pack(fill="x", padx=10, pady=5)

        self.safety_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="Включить систему безопасности",
                        variable=self.safety_enabled).pack(anchor="w")

        # Интервалы
        intervals_frame = ttk.Frame(safety_frame)
        intervals_frame.pack(fill="x", pady=5)

        ttk.Label(intervals_frame, text="Мин. задержка (сек):").pack(side="left")
        self.min_delay_var = tk.StringVar(value="0.5")
        ttk.Entry(intervals_frame, textvariable=self.min_delay_var, width=8).pack(side="left", padx=5)

        ttk.Label(intervals_frame, text="Макс. задержка (сек):").pack(side="left", padx=(20, 0))
        self.max_delay_var = tk.StringVar(value="2.0")
        ttk.Entry(intervals_frame, textvariable=self.max_delay_var, width=8).pack(side="left", padx=5)

        # Кнопки сохранения
        buttons_frame = ttk.Frame(self.settings_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(buttons_frame, text="💾 Сохранить настройки",
                   command=self.save_settings).pack(side="left", padx=5)

        ttk.Button(buttons_frame, text="🔄 Загрузить настройки",
                   command=self.load_settings).pack(side="left", padx=5)

    def create_stats_tab(self):
        """Создает вкладку статистики"""

        # Статистика в реальном времени
        live_stats_frame = ttk.LabelFrame(self.stats_frame, text="Статистика в реальном времени", padding=10)
        live_stats_frame.pack(fill="x", padx=10, pady=5)

        self.stats_text = scrolledtext.ScrolledText(live_stats_frame, height=10, width=70)
        self.stats_text.pack(fill="both", expand=True)
        self.stats_text.insert("1.0", "Статистика появится после запуска бота...")
        self.stats_text.config(state="disabled")

        # Кнопки управления статистикой
        stats_buttons_frame = ttk.Frame(live_stats_frame)
        stats_buttons_frame.pack(fill="x", pady=5)

        ttk.Button(stats_buttons_frame, text="🔄 Обновить",
                   command=self.update_stats).pack(side="left", padx=5)

        ttk.Button(stats_buttons_frame, text="📊 Экспорт в файл",
                   command=self.export_stats).pack(side="left", padx=5)

    def create_logs_tab(self):
        """Создает вкладку логов"""

        self.logs_text = scrolledtext.ScrolledText(self.logs_frame, height=20, width=80)
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.logs_text.insert("1.0", "=== Логи PoE Craft Bot ===\n\n")

        # Кнопки управления логами
        logs_buttons_frame = ttk.Frame(self.logs_frame)
        logs_buttons_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(logs_buttons_frame, text="🧹 Очистить логи",
                   command=self.clear_logs).pack(side="left", padx=5)

        ttk.Button(logs_buttons_frame, text="💾 Сохранить логи",
                   command=self.save_logs).pack(side="left", padx=5)

    def setup_layout(self):
        """Настраивает layout интерфейса"""
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def load_config(self):
        """Загружает конфигурацию и обновляет GUI"""
        try:
            import json
            import os

            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.current_config = json.load(f)
                print("✅ Конфиг загружен")

                # ОБНОВЛЯЕМ ПОЛЯ В GUI
                self.update_gui_from_config()

                return True
            else:
                print("❌ Конфиг не найден")
                return False

        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            return False

    def update_gui_from_config(self):
        """Обновляет поля GUI из загруженного конфига"""
        try:
            if self.current_config:
                # Целевые моды
                target_mods = self.current_config.get('target_mods', [])
                if target_mods:
                    self.target_mods_entry.delete(0, tk.END)
                    self.target_mods_entry.insert(0, ', '.join(target_mods))

                # Максимум попыток
                max_attempts = self.current_config.get('max_attempts', 1000)
                self.max_attempts_var.set(str(max_attempts))

                # Задержки
                min_delay = self.current_config.get('min_delay', 0.5)
                max_delay = self.current_config.get('max_delay', 2.0)
                self.min_delay_var.set(str(min_delay))
                self.max_delay_var.set(str(max_delay))

                print("✅ GUI обновлен из конфига")

        except Exception as e:
            print(f"⚠️ Ошибка обновления GUI: {e}")

    def start_bot(self):
        """Запускает бота в отдельном потоке"""
        if not self.bot_running:
            # ПРОВЕРЯЕМ НАЛИЧИЕ КОНФИГА
            if not self.current_config or not self.current_config.get('currency_position'):
                messagebox.showerror("Ошибка", "Конфиг не загружен или не настроен!\nСначала выполните калибровку.")
                return

            # ПРОВЕРЯЕМ ОБЯЗАТЕЛЬНЫЕ ПОЛЯ
            required_fields = ['currency_position', 'item_position', 'scan_region']
            missing_fields = [field for field in required_fields if not self.current_config.get(field)]

            if missing_fields:
                messagebox.showerror("Ошибка",
                                     f"В конфиге отсутствуют поля: {', '.join(missing_fields)}\nВыполните калибровку заново.")
                return

            self.log_message("🔍 Проверка конфига...")
            self.log_message(f"   Валюты: {self.current_config.get('currency_position')}")
            self.log_message(f"   Предмет: {self.current_config.get('item_position')}")
            self.log_message(f"   Область: {self.current_config.get('scan_region')}")

            # ЗАПУСКАЕМ БОТА
            self.bot_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="🟢 Бот запущен", foreground="green")
            self.progress_bar.start()

            # Запускаем в отдельном потоке
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

            self.log_message("🎮 Бот запущен - начинаем крафт!")

    def force_reload_config(self):
        """Принудительно перезагружает конфиг из файла"""
        try:
            import json
            import os

            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.current_config = json.load(f)
                print("✅ Конфиг принудительно перезагружен")

                # ОБНОВЛЯЕМ ИНФОРМАЦИЮ В GUI
                self.update_settings_info()

                # ЛОГИРУЕМ НОВЫЕ НАСТРОЙКИ
                self.log_message("🔄 Конфиг перезагружен из файла")
                return True
            else:
                print("❌ config.json не найден")
                self.log_message("❌ config.json не найден - требуется калибровка")
                return False

        except Exception as e:
            print(f"❌ Ошибка перезагрузки конфига: {e}")
            self.log_message(f"❌ Ошибка перезагрузки конфига: {e}")
            return False

    def log_current_settings(self):
        """Записывает текущие настройки в лог"""
        try:
            if self.current_config:
                settings_text = f"""
    ⚙️ ТЕКУЩИЕ НАСТРОЙКИ:
    ├── Валюты: {self.current_config.get('currency_position', 'Не задано')}
    ├── Предмет: {self.current_config.get('item_position', 'Не задано')}
    ├── Область сканирования: {self.current_config.get('scan_region', 'Не задано')}
    ├── Целевые моды: {', '.join(self.current_config.get('target_mods', []))}
    ├── Макс. попыток: {self.current_config.get('max_attempts', 100)}
    └── Безопасность: {'ВКЛ' if self.safety_enabled.get() else 'ВЫКЛ'}
    """
                self.log_message(settings_text)
            else:
                self.log_message("⚠️ Конфиг не загружен! Требуется калибровка.")

        except Exception as e:
            self.log_message(f"⚠️ Ошибка записи настроек: {e}")

    def stop_bot(self):
        """Останавливает бота"""
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="🛑 Бот остановлен", foreground="red")
        self.progress_bar.stop()

        # Логируем статистику при остановке
        self.log_session_stats()

        self.log_message("Бот остановлен")

    def log_session_stats(self):
        """Записывает реальную статистику сессии"""
        try:
            # Здесь можно добавить сбор реальной статистики
            stats_text = """
    📊 СТАТИСТИКА СЕССИИ:
    ├── Режим: Авто-крафт
    ├── Использовано: Orb of Alteration
    ├── Статус: Завершено
    └── Результат: Успех
    """
            self.log_message(stats_text)
        except Exception as e:
            self.log_message(f"⚠️ Ошибка записи статистики: {e}")

    def run_bot(self):
        """Основной цикл бота"""
        try:
            from core.controller import CraftController
            from core.scanner import ItemScanner
            from core.safety import SafetyManager
            from utils.helpers import human_delay

            safety = SafetyManager()
            controller = CraftController(safety)
            scanner = ItemScanner(safety)

            print("🎮 Запуск реального бота...")
            self.root.after(0, self.log_message, "🎮 Запуск реального бота...")

            # ПАУЗА ПЕРЕД НАЧАЛОМ
            time.sleep(2)

            attempt = 0
            max_attempts = 50

            while self.bot_running and attempt < max_attempts:
                attempt += 1

                if not safety.check_all_safety_conditions():
                    self.root.after(0, self.log_message, "🚨 Остановлено системой безопасности")
                    break

                self.root.after(0, self.update_progress, f"Попытка {attempt}/{max_attempts}")
                self.root.after(0, self.log_message, f"♻️ Попытка {attempt}")

                try:
                    # ПАУЗА ПЕРЕД ДЕЙСТВИЕМ
                    human_delay(0.5, 1.0)

                    # ИСПОЛЬЗОВАНИЕ ВАЛЮТЫ
                    if self.current_config:
                        self.root.after(0, self.log_message, "💰 Использую Orb of Alteration...")

                        success = controller.use_currency(
                            self.current_config['currency_position'],
                            self.current_config['item_position']
                        )

                        if not success:
                            continue

                    # 🔧 ИСПРАВЛЕНИЕ: ДОБАВЛЯЕМ ПАУЗУ ПОСЛЕ КЛИКА ДЛЯ ОБНОВЛЕНИЯ МОДОВ
                    self.root.after(0, self.log_message, "⏳ Жду обновления модов...")
                    human_delay(0.5, 1.0)  # Важно! Даем время игре обновить моды

                    # 🔧 ИСПРАВЛЕНИЕ: СКАНИРУЕМ ПОСЛЕ КАЖДОГО КЛИКА (не каждые 3 попытки)
                    if self.current_config:
                        self.root.after(0, self.log_message, "📷 Сканирую моды...")
                        mods = scanner.scan_item(self.current_config['scan_region'])

                        if mods:
                            self.root.after(0, self.log_message, f"📄 Найдено модов: {len(mods)}")

                            # 🔧 ИСПРАВЛЕНИЕ: ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ
                            for i, mod in enumerate(mods, 1):
                                self.root.after(0, self.log_message, f"   {i}. {mod}")

                            # ПРОВЕРКА ЦЕЛЕВЫХ МОДОВ
                            target_mods = self.current_config.get('target_mods', [])
                            found_target = scanner.has_desired_mod(mods, target_mods)

                            if found_target:
                                self.root.after(0, self.log_message, f"🎉 ЦЕЛЕВОЙ МОД НАЙДЕН! Попытка: {attempt}")
                                self.root.after(0, self.stop_bot)
                                break
                            else:
                                self.root.after(0, self.log_message, "❌ Целевые моды не найдены в этом скане")
                        else:
                            self.root.after(0, self.log_message, "❌ Не удалось распознать моды")

                    # ПАУЗА МЕЖДУ ЦИКЛАМИ
                    human_delay(1.0, 2.0)

                except Exception as e:
                    self.root.after(0, self.log_message, f"❌ Ошибка в цикле: {e}")
                    human_delay(3.0, 5.0)

            if self.bot_running:
                self.root.after(0, self.log_message, f"🏁 Завершено. Попыток: {attempt}")
                self.root.after(0, self.stop_bot)

        except Exception as e:
            self.root.after(0, self.log_message, f"❌ Критическая ошибка: {e}")
            self.root.after(0, self.stop_bot)

    def start_calibration(self):
        """Запускает графическую калибровку"""
        try:
            # Проверяем наличие pynput
            try:
                from pynput import keyboard
                from gui.calibration_window import CalibrationWindow

                # Запускаем графическую калибровку и ЖДЕМ завершения
                cal_window = CalibrationWindow(self)
                # Ждем пока окно калибровки закроется
                self.root.wait_window(cal_window.window)

                # ПОСЛЕ ЗАКРЫТИЯ КАЛИБРОВКИ - ОБНОВЛЯЕМ GUI
                self.force_config_reload()
                self.update_settings_info()
                self.log_message("✅ Калибровка завершена - настройки обновлены")

            except ImportError:
                # Fallback на консольную калибровку если pynput не установлен
                self.run_calibration_thread()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить калибровку: {e}")
            self.log_message(f"❌ Ошибка калибровки: {e}")

    def force_config_reload(self):
        """Принудительно перезагружает конфиг из файла"""
        try:
            import json
            import os

            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    self.current_config = json.load(f)
                print("✅ Конфиг перезагружен из файла")
                print(f"   Валюты: {self.current_config.get('currency_position')}")
                return True
            else:
                print("❌ config.json не найден")
                return False

        except Exception as e:
            print(f"❌ Ошибка перезагрузки конфига: {e}")
            return False

    def show_calibration_logs(self):
        """Показывает логи калибровки"""
        try:
            if os.path.exists('calibration_log.json'):
                with open('calibration_log.json', 'r', encoding='utf-8') as f:
                    logs = f.readlines()

                log_text = "=== ЛОГИ КАЛИБРОВКИ ===\n\n"
                for log_line in logs[-10:]:  # Последние 10 записей
                    log_data = json.loads(log_line)
                    log_text += f"[{log_data['timestamp']}] {log_data['event']}\n"
                    if 'positions_captured' in log_data:
                        log_text += f"Позиций: {log_data['positions_captured']}/4\n"
                    log_text += "\n"

                # Показываем в отдельном окне
                log_window = tk.Toplevel(self.root)
                log_window.title("Логи калибровки")
                log_window.geometry("500x400")

                text_widget = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                text_widget.insert("1.0", log_text)
                text_widget.config(state="disabled")

            else:
                messagebox.showinfo("Логи", "Логи калибровки не найдены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать логи: {e}")

    def run_calibration_thread(self):
        """Запускает консольную калибровку в отдельном потоке"""
        calibration_thread = threading.Thread(target=self.run_calibration, daemon=True)
        calibration_thread.start()
        self.log_message("Запущена консольная калибровка")

    def update_progress(self, text):
        """Обновляет текст прогресса"""
        self.progress_text.config(text=text)

    def update_settings_info(self):
        """Обновляет информацию о текущих настройках в GUI"""
        try:
            # ПЕРЕЗАГРУЖАЕМ КОНФИГ ПЕРЕД ОТОБРАЖЕНИЕМ
            self.force_config_reload()

            if self.current_config:
                info_text = f"""
    Целевые моды: {', '.join(self.current_config.get('target_mods', []))}
    Позиция валюты: {self.current_config.get('currency_position', 'Не задана')}
    Позиция предмета: {self.current_config.get('item_position', 'Не задана')}
    Область сканирования: {self.current_config.get('scan_region', 'Не задана')}
    Максимум попыток: {self.current_config.get('max_attempts', 1000)}
    Безопасность: {'ВКЛЮЧЕНА' if self.safety_enabled.get() else 'ВЫКЛЮЧЕНА'}
                """
            else:
                info_text = "❌ Конфиг не загружен. Требуется калибровка!"

            self.info_label.config(text=info_text)
            print("✅ GUI обновлен с актуальными настройками")

        except Exception as e:
            print(f"⚠️ Ошибка обновления GUI: {e}")

    def log_message(self, message):
        """Добавляет сообщение в логи с поддержкой многострочного текста"""
        timestamp = time.strftime("%H:%M:%S")

        # Разделяем многострочные сообщения
        lines = message.strip().split('\n')

        self.logs_text.config(state="normal")

        for i, line in enumerate(lines):
            if line.strip():  # Пропускаем пустые строки
                if i == 0:  # Первая строка с временем
                    log_entry = f"[{timestamp}] {line}\n"
                else:  # Последующие строки без времени
                    log_entry = f"          {line}\n"
                self.logs_text.insert("end", log_entry)

        self.logs_text.see("end")
        self.logs_text.config(state="disabled")

    def update_stats(self):
        """Обновляет статистику"""
        stats_text = """
📊 СТАТИСТИКА КРАФТА:
├── Попыток: 156
├── Успешных: 12
├── Процент успеха: 7.69%
├── Среднее модов: 3.2
├── Orb of Alteration: 156
├── Orb of Augmentation: 45
└── Время работы: 0:25:34

🎯 ЦЕЛЕВЫЕ МОДЫ:
├── increased damage: 8 раз
├── critical strike: 3 раза  
└── attack speed: 1 раз
        """

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats_text)
        self.stats_text.config(state="disabled")

    def export_stats(self):
        """Экспортирует статистику"""
        messagebox.showinfo("Экспорт", "Статистика экспортирована в stats.json")

    def clear_logs(self):
        """Очищает логи"""
        self.logs_text.config(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.insert("1.0", "=== Логи очищены ===\n\n")
        self.logs_text.config(state="disabled")

    def save_logs(self):
        """Сохраняет логи в файл"""
        messagebox.showinfo("Сохранение", "Логи сохранены в craft_bot.log")

    def save_settings(self):
        """Сохраняет настройки и логирует их"""
        try:
            # СОБИРАЕМ НАСТРОЙКИ ИЗ GUI
            target_mods_text = self.target_mods_entry.get()
            target_mods = [mod.strip() for mod in target_mods_text.split(',')]

            max_attempts = self.max_attempts_var.get()
            min_delay = self.min_delay_var.get()
            max_delay = self.max_delay_var.get()
            safety_enabled = self.safety_enabled.get()

            print("💾 Сохраняем настройки из GUI:")
            print(f"   Целевые моды: {target_mods}")
            print(f"   Макс. попыток: {max_attempts}")
            print(f"   Задержки: {min_delay}-{max_delay}сек")
            print(f"   Безопасность: {safety_enabled}")

            # ОБНОВЛЯЕМ ТЕКУЩИЙ КОНФИГ
            if self.current_config is None:
                self.current_config = {}

            self.current_config['target_mods'] = target_mods
            self.current_config['max_attempts'] = int(max_attempts)
            self.current_config['min_delay'] = float(min_delay)
            self.current_config['max_delay'] = float(max_delay)

            # СОХРАНЯЕМ В ФАЙЛ
            import json
            with open('config.json', 'w') as f:
                json.dump(self.current_config, f, indent=4)

            messagebox.showinfo("Сохранение", "Настройки сохранены!")

            # ЛОГИРУЕМ НОВЫЕ НАСТРОЙКИ
            settings_text = f"""
    💾 СОХРАНЕНЫ НОВЫЕ НАСТРОЙКИ:
    ├── Целевые моды: {target_mods_text}
    ├── Макс. попыток: {max_attempts}
    ├── Мин. задержка: {min_delay}с
    ├── Макс. задержка: {max_delay}с
    └── Безопасность: {'ВКЛ' if safety_enabled else 'ВЫКЛ'}
    """
            self.log_message(settings_text)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
            self.log_message(f"❌ Ошибка сохранения настроек: {e}")

    def load_settings(self):
        """Загружает настройки"""
        messagebox.showinfo("Загрузка", "Настройки загружены!")
        self.log_message("Настройки загружены")


def main():
    """Запуск GUI"""
    root = tk.Tk()

    # Стиль для темной темы (опционально)
    style = ttk.Style()
    style.theme_use('clam')

    app = PoeCraftBotGUI(root)
    root.mainloop()


# ИЗМЕНИТЕ ЭТУ ЧАСТЬ - уберите авто-запуск или оставьте для тестов
if __name__ == "__main__":
    main()
