import tkinter as tk
from tkinter import ttk
from ..widgets import StatusPanel, ControlButtons


class MainTab(ttk.Frame):
    """Главная вкладка интерфейса"""

    def __init__(self, parent, start_callback, stop_callback, calibrate_callback):
        super().__init__(parent)
        self.parent = parent

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.calibrate_callback = calibrate_callback

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы главной вкладки"""
        # Заголовок
        title_label = ttk.Label(
            self,
            text="Path of Exile Craft Bot",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        # Панель статуса
        self.status_panel = StatusPanel(self, "Статус бота")
        self.status_panel.pack(fill="x", padx=10, pady=5)

        # Панель кнопок управления
        self.control_buttons = ControlButtons(
            self,
            self.start_clicked,
            self.stop_clicked,
            self.calibrate_clicked
        )
        self.control_buttons.pack(fill="x", padx=10, pady=5)

        # Информация о настройках
        self.info_frame = ttk.LabelFrame(self, text="Текущие настройки", padding=10)
        self.info_frame.pack(fill="x", padx=10, pady=5)

        self.info_label = ttk.Label(
            self.info_frame,
            text="Загрузите конфиг для отображения настроек...",
            justify="left"
        )
        self.info_label.pack(anchor="w")

    def start_clicked(self):
        """Обработчик нажатия кнопки запуска"""
        self.status_panel.set_running()
        self.control_buttons.set_running_state()
        self.status_panel.set_progress_text("Запуск бота...")
        self.start_callback()

    def stop_clicked(self):
        """Обработчик нажатия кнопки остановки"""
        self.status_panel.set_stopped()
        self.control_buttons.set_stopped_state()
        self.status_panel.set_progress_text("Остановка...")
        self.stop_callback()

    def calibrate_clicked(self):
        """Обработчик нажатия кнопки калибровки"""
        self.calibrate_callback()

    def update_info(self, config_text):
        """Обновляет информацию о настройках"""
        self.info_label.config(text=config_text)

    def set_progress_text(self, text):
        """Устанавливает текст прогресса"""
        self.status_panel.set_progress_text(text)
