import tkinter as tk
from tkinter import ttk, scrolledtext
import time


class LogDisplay(ttk.LabelFrame):
    """Отображение логов"""

    def __init__(self, parent, title="Логи"):
        super().__init__(parent, text=title, padding=10)
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы отображения логов"""
        # Текстовое поле для логов
        self.logs_text = scrolledtext.ScrolledText(
            self,
            height=15,
            width=80,
            wrap=tk.WORD
        )
        self.logs_text.pack(fill="both", expand=True)
        self.logs_text.insert("1.0", "=== Логи PoE Craft Bot ===\n\n")
        self.logs_text.config(state="disabled")

        # Панель кнопок управления логами
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.pack(fill="x", pady=5)

        # Кнопка очистки логов
        self.clear_button = ttk.Button(
            self.buttons_frame,
            text="🧹 Очистить логи",
            command=self.clear_logs
        )
        self.clear_button.pack(side="left", padx=5)

        # Кнопка сохранения логов
        self.save_button = ttk.Button(
            self.buttons_frame,
            text="💾 Сохранить логи",
            command=self.save_logs
        )
        self.save_button.pack(side="left", padx=5)

    def add_message(self, message):
        """Добавляет сообщение в логи"""
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

    def clear_logs(self):
        """Очищает логи"""
        self.logs_text.config(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.insert("1.0", "=== Логи очищены ===\n\n")
        self.logs_text.config(state="disabled")

    def save_logs(self):
        """Сохраняет логи в файл"""
        try:
            self.logs_text.config(state="normal")
            log_content = self.logs_text.get("1.0", "end-1c")
            self.logs_text.config(state="disabled")

            with open('craft_bot.log', 'w', encoding='utf-8') as f:
                f.write(log_content)

            self.add_message("💾 Логи сохранены в craft_bot.log")
        except Exception as e:
            self.add_message(f"❌ Ошибка сохранения логов: {e}")
