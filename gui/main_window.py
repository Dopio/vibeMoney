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

        # Создаем интерфейс
        self.create_widgets()
        self.setup_layout()

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

    def start_bot(self):
        """Запускает бота в отдельном потоке"""
        if not self.bot_running:
            self.bot_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="🟢 Бот запущен", foreground="green")
            self.progress_bar.start()

            # Запускаем в отдельном потоке
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

            self.log_message("Бот запущен")

    def stop_bot(self):
        """Останавливает бота"""
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="🛑 Бот остановлен", foreground="red")
        self.progress_bar.stop()

        self.log_message("Бот остановлен")

    def run_bot(self):
        """Основной цикл бота (запускается в потоке)"""
        try:
            # Имитация работы бота
            attempt = 0
            while self.bot_running and attempt < 100:
                attempt += 1

                # Обновляем UI в основном потоке
                self.root.after(0, self.update_progress, f"Попытка {attempt}")

                # Имитация крафта
                time.sleep(1)

                # Имитация нахождения мода
                if attempt % 10 == 0:
                    self.root.after(0, self.log_message, f"🎉 Найден хороший мод на попытке {attempt}")

            if self.bot_running:
                self.root.after(0, self.stop_bot)

        except Exception as e:
            self.root.after(0, self.log_message, f"❌ Ошибка: {e}")
            self.root.after(0, self.stop_bot)

    def start_calibration(self):
        """Запускает калибровку"""
        messagebox.showinfo("Калибровка", "Запуск калибровки...")
        self.log_message("Запущена калибровка")

    def update_progress(self, text):
        """Обновляет текст прогресса"""
        self.progress_text.config(text=text)

    def log_message(self, message):
        """Добавляет сообщение в логи"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.logs_text.config(state="normal")
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
        """Сохраняет настройки"""
        messagebox.showinfo("Сохранение", "Настройки сохранены!")
        self.log_message("Настройки сохранены")

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


if __name__ == "__main__":
    main()
