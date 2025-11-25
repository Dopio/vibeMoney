import tkinter as tk
from tkinter import ttk, messagebox


class MassCraftTab(ttk.Frame):
    def __init__(self, parent, start_callback=None, stop_callback=None, config_callback=None):
        super().__init__(parent)
        self.status_label = None
        self.progress_bar = None
        self.progress_var = None
        self.start_btn = None
        self.stop_btn = None
        self.items_info_label = None
        self.max_attempts_entry = None
        self.target_mods_entry = None
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.config_callback = config_callback
        self.create_widgets()

    def create_widgets(self):
        """Создает элементы интерфейса массового крафта"""
        # Заголовок
        title_label = ttk.Label(self, text="🔄 Массовый крафт", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Фрейм настроек
        settings_frame = ttk.LabelFrame(self, text="Настройки массового крафта", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Целевые моды
        (ttk.Label(settings_frame, text="Целевые моды (через запятую):")
         .grid(row=0, column=0, sticky="w", pady=5))

        self.target_mods_entry = ttk.Entry(settings_frame, width=50)
        self.target_mods_entry.grid(row=0, column=1, padx=5, pady=5)

        # Максимум попыток на предмет
        (ttk.Label(settings_frame, text="Макс. попыток на предмет:")
         .grid(row=1, column=0, sticky="w", pady=5))

        self.max_attempts_entry = ttk.Entry(settings_frame, width=10)
        self.max_attempts_entry.insert(0, "50")
        self.max_attempts_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Информация о предметах
        self.items_info_label = ttk.Label(settings_frame, text="Слотов предметов: 0")
        self.items_info_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # Фрейм управления
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Кнопки управления
        self.start_btn = ttk.Button(
            control_frame, 
            text="🚀 Начать массовый крафт", 
            command=self.start_mass_craft
        )
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(
            control_frame, 
            text="⏹️ Остановить", 
            command=self.stop_mass_craft,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)

        # Прогресс
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=5)

        self.status_label = ttk.Label(self, text="Готов к работе")
        self.status_label.pack(pady=5)

    def start_mass_craft(self):
        """Запуск массового крафта"""
        if self.start_callback:
            target_mods = self.get_target_mods()
            max_attempts = self.get_max_attempts()
            self.start_callback(target_mods, max_attempts)

    def stop_mass_craft(self):
        """Остановка массового крафта"""
        if self.stop_callback:
            self.stop_callback()

    def get_target_mods(self):
        """Получает целевые моды из поля ввода и сохраняет в конфиг"""
        text = self.target_mods_entry.get().strip()
        if not text:
            messagebox.showerror("Ошибка", "Введите целевые моды")
            return None

        target_mods = [mod.strip() for mod in text.split(',')]

        # Сохраняем в конфиг (с проверкой на None)
        if self.config_callback and callable(self.config_callback):
            self.config_callback('target_mods', target_mods)

        return target_mods

    def set_target_mods(self, target_mods):
        """Устанавливает целевые моды из конфига"""
        if target_mods and isinstance(target_mods, list):
            self.target_mods_entry.delete(0, tk.END)
            self.target_mods_entry.insert(0, ', '.join(target_mods))

    def get_max_attempts(self):
        """Получает максимальное количество попыток"""
        try:
            return int(self.max_attempts_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное количество попыток")
            return None

    def update_items_info(self, item_count):
        """Обновляет информацию о предметах"""
        self.items_info_label.config(text=f"Слотов предметов: {item_count}")

    def set_running_state(self, status_text):
        """Устанавливает состояние 'работает'"""
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text=status_text)

    def set_stopped_state(self, status_text):
        """Устанавливает состояние 'остановлен'"""
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text=status_text)

    def update_progress(self, progress, current_item, total_items):
        """Обновляет прогресс"""
        self.progress_var.set(progress)
        self.status_label.config(text=f"Обработано: {current_item}/{total_items} предметов")
