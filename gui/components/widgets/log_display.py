import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import datetime


class LogDisplay(ttk.Frame):
    def __init__(self, parent, clear_callback=None, save_callback=None):
        super().__init__(parent)
        self.clear_callback = clear_callback
        self.save_callback = save_callback

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы интерфейса логов"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        title = ttk.Label(main_frame, text="📝 Логи работы бота", font=('Arial', 14, 'bold'))
        title.pack(pady=(0, 10))

        # Область логов
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=20,
            width=80,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True, pady=(0, 10))

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="🧹 Очистить",
                   command=self._on_clear_clicked).pack(side="left", padx=5)
        ttk.Button(button_frame, text="💾 Сохранить",
                   command=self._on_save_clicked).pack(side="left", padx=5)

        # Начальное сообщение
        self.add_message("🚀 Логгер инициализирован. Готов к работе!")

    def _on_clear_clicked(self):
        """Обработчик очистки логов"""
        if self.clear_callback:
            self.clear_callback()
        else:
            self.clear_logs()

    def _on_save_clicked(self):
        """Обработчик сохранения логов"""
        if self.save_callback:
            self.save_callback()
        else:
            self.save_logs()

    def add_message(self, message):
        """Добавляет сообщение в логи"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Автопрокрутка к новому сообщению

    def clear_logs(self):
        """Очищает логи"""
        self.log_text.delete(1.0, tk.END)
        self.add_message("🧹 Логи очищены")

    def save_logs(self):
        """Сохраняет логи в файл"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.add_message(f"💾 Логи сохранены в {filename}")
        except Exception as e:
            self.add_message(f"❌ Ошибка сохранения логов: {e}")