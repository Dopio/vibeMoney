import tkinter as tk
from tkinter import ttk


class ControlButtons(ttk.Frame):
    """Панель кнопок управления"""

    def __init__(self, parent, start_callback, stop_callback, calibrate_callback):
        super().__init__(parent)
        self.parent = parent

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.calibrate_callback = calibrate_callback

        self.create_widgets()

    def create_widgets(self):
        """Создает кнопки управления"""
        # Кнопка запуска
        self.start_button = ttk.Button(
            self,
            text="▶️ Запуск бота",
            command=self.start_callback,
            style="Accent.TButton"
        )
        self.start_button.pack(side="left", padx=5)

        # Кнопка остановки
        self.stop_button = ttk.Button(
            self,
            text="⏹️ Остановить",
            command=self.stop_callback,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        # Кнопка калибровки
        self.calibrate_button = ttk.Button(
            self,
            text="🎯 Калибровка",
            command=self.calibrate_callback
        )
        self.calibrate_button.pack(side="left", padx=5)

    def set_running_state(self):
        """Устанавливает состояние 'бот запущен'"""
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

    def set_stopped_state(self):
        """Устанавливает состояние 'бот остановлен'"""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
