from tkinter import ttk


class ControlButtons(ttk.Frame):
    """Панель кнопок управления"""

    def __init__(self,
                 parent,
                 start_callback,
                 stop_callback,
                 calibrate_callback,
                 calibrate_stash_callback=None):
        super().__init__(parent)
        self.stash_calibrate_button = None
        self.calibrate_button = None
        self.stop_button = None
        self.start_button = None
        self.parent = parent

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.calibrate_callback = calibrate_callback
        self.calibrate_stash_callback = calibrate_stash_callback

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
            text="🎯 Калибровка позиций",
            command=self.calibrate_callback
        )
        self.calibrate_button.pack(side="left", padx=5)

        # Кнопка калибровки вкладки
        self.stash_calibrate_button = ttk.Button(
            self,
            text="📦 Калибровка вкладки",
            command=self.calibrate_stash_callback if self.calibrate_stash_callback else self.calibrate_callback
        )
        self.stash_calibrate_button.pack(side="left", padx=5)

    def set_running_state(self):
        """Устанавливает состояние 'бот запущен'"""
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

    def set_stopped_state(self):
        """Устанавливает состояние 'бот остановлен'"""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
