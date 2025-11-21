import tkinter as tk
from tkinter import ttk


class MainTab(ttk.Frame):
    def __init__(self, parent, start_callback=None, stop_callback=None, calibrate_callback=None):
        super().__init__(parent)
        self.info_text = None
        self.stop_button = None
        self.start_button = None
        self.progress_var = None
        self.status_var = None
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.calibrate_callback = calibrate_callback

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы интерфейса главной вкладки"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        title = ttk.Label(main_frame, text="🎮 Управление ботом", font=('Arial', 16, 'bold'))
        title.pack(pady=(0, 20))

        # Статус бота
        self.status_var = tk.StringVar(value="🛑 Бот остановлен")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Arial', 12))
        status_label.pack(pady=(0, 10))

        # Прогресс
        self.progress_var = tk.StringVar(value="Готов к работе")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var, font=('Arial', 10))
        progress_label.pack(pady=(0, 20))

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="🚀 Запуск",
            command=self.start_clicked,
            style='Accent.TButton'
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(
            button_frame,
            text="🛑 Стоп",
            command=self.stop_clicked,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="🎯 Калибровка",
            command=self.calibrate_clicked
        ).pack(side="left", padx=5)

        # Информация о конфиге
        self.info_text = tk.Text(main_frame, height=8, width=60, font=('Consolas', 9))
        self.info_text.pack(fill="both", expand=True, pady=10)

    def start_clicked(self):
        """Обработчик запуска бота"""
        if self.start_callback:
            self.start_callback()

    def stop_clicked(self):
        """Обработчик остановки бота"""
        if self.stop_callback:
            self.stop_callback()

    def calibrate_clicked(self):
        """Обработчик калибровки"""
        if self.calibrate_callback:
            self.calibrate_callback()

    # ДОБАВЛЯЕМ НУЖНЫЕ МЕТОДЫ:
    def set_running_state(self, message="Бот запущен"):
        """Устанавливает состояние 'запущен'"""
        self.status_var.set("🟢 " + message)
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

    def set_stopped_state(self, message="Бот остановлен"):
        """Устанавливает состояние 'остановлен'"""
        self.status_var.set("🛑 " + message)
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def set_progress_text(self, text):
        """Устанавливает текст прогресса"""
        self.progress_var.set(text)

    def update_info(self, info_text):
        """Обновляет информацию о конфиге"""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
