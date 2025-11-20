import tkinter as tk
from tkinter import ttk


class StatsTab(ttk.Frame):
    def __init__(self, parent, update_callback=None, export_callback=None):
        super().__init__(parent)
        self.update_callback = update_callback
        self.export_callback = export_callback

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы интерфейса статистики"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        title = ttk.Label(main_frame, text="📊 Статистика крафта", font=('Arial', 14, 'bold'))
        title.pack(pady=(0, 15))

        # Область статистики
        self.stats_text = tk.Text(main_frame, height=15, width=60, font=('Consolas', 10))
        self.stats_text.pack(fill="both", expand=True, pady=(0, 10))

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="🔄 Обновить",
                   command=self.update_stats).pack(side="left", padx=5)
        ttk.Button(button_frame, text="📤 Экспорт",
                   command=self.export_stats).pack(side="left", padx=5)

        # Начальное сообщение
        self.update_stats("Запустите бота для сбора статистики...")

    def update_stats(self, stats_text=None):
        """Обновляет статистику"""
        if stats_text:
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_text)
        elif self.update_callback:
            self.update_callback()

    def export_stats(self):
        """Экспортирует статистику"""
        if self.export_callback:
            self.export_callback()
