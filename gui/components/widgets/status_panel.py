import tkinter as tk
from tkinter import ttk


class StatusPanel(ttk.LabelFrame):
    """Панель статуса бота"""

    def __init__(self, parent, title="Статус бота"):
        super().__init__(parent, text=title, padding=10)
        self.parent = parent

        self.status_var = tk.StringVar(value="🛑 Остановлен")
        self.status_color = "red"

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы панели статуса"""
        # Статус
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            font=("Arial", 12, "bold"),
            foreground=self.status_color
        )
        self.status_label.pack()

        # Прогресс бар
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=5)

        # Текст прогресса
        self.progress_text = ttk.Label(self, text="Ожидание запуска...")
        self.progress_text.pack()

    def set_running(self):
        """Устанавливает статус 'Запущен'"""
        self.status_var.set("🟢 Запущен")
        self.status_label.config(foreground="green")
        self.progress_bar.start()

    def set_stopped(self):
        """Устанавливает статус 'Остановлен'"""
        self.status_var.set("🛑 Остановлен")
        self.status_label.config(foreground="red")
        self.progress_bar.stop()

    def set_progress_text(self, text):
        """Устанавливает текст прогресса"""
        self.progress_text.config(text=text)
