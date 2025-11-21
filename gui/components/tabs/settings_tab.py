import tkinter as tk
from tkinter import ttk


class SettingsTab(ttk.Frame):
    def __init__(self, parent, save_callback=None, load_callback=None):
        super().__init__(parent)
        self.max_delay = None
        self.min_delay = None
        self.preprocess = None
        self.emergency_stop = None
        self.target_mods = None
        self.max_attempts = None
        self.mouse_safety = None
        self.confidence = None
        self.save_callback = save_callback
        self.load_callback = load_callback

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы интерфейса настроек"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Настройки бота
        self.create_bot_settings(main_frame)

        # Настройки безопасности
        self.create_safety_settings(main_frame)

        # Настройки сканирования
        self.create_scan_settings(main_frame)

        # Кнопки управления
        self.create_control_buttons(main_frame)

    def create_bot_settings(self, parent):
        """Настройки бота"""
        bot_frame = ttk.LabelFrame(parent, text="🤖 Настройки бота", padding=10)
        bot_frame.pack(fill="x", pady=(0, 10))

        # Сетка для упорядоченного размещения
        row = 0

        # Максимум попыток
        ttk.Label(bot_frame, text="Максимум попыток:").grid(row=0, column=0, sticky="w", pady=2)
        self.max_attempts = ttk.Spinbox(bot_frame, from_=1, to=10000, width=10)
        self.max_attempts.grid(row=0, column=1, sticky="w", pady=2, padx=(10, 0))
        row += 1

        ttk.Label(bot_frame, text="Целевые моды:").grid(row=1, column=0, sticky="nw", pady=2)
        self.target_mods = tk.Text(bot_frame, height=4, width=30)
        self.target_mods.grid(row=1, column=1, sticky="w", pady=2, padx=(10, 0))
        row += 1

        # Минимальная задержка (НОВАЯ НАСТРОЙКА)
        ttk.Label(bot_frame, text="Мин. задержка (сек):").grid(row=row, column=0, sticky="w", pady=2)
        self.min_delay = ttk.Spinbox(bot_frame, from_=0.1, to=5.0, increment=0.1, width=10)
        self.min_delay.set(0.3)
        self.min_delay.grid(row=row, column=1, sticky="w", pady=2, padx=(10, 0))
        row += 1

        # Максимальная задержка (НОВАЯ НАСТРОЙКА)
        ttk.Label(bot_frame, text="Макс. задержка (сек):").grid(row=row, column=0, sticky="w", pady=2)
        self.max_delay = ttk.Spinbox(bot_frame, from_=0.1, to=5.0, increment=0.1, width=10)
        self.max_delay.set(0.5)
        self.max_delay.grid(row=row, column=1, sticky="w", pady=2, padx=(10, 0))
        row += 1

    def create_safety_settings(self, parent):
        """Настройки безопасности"""
        safety_frame = ttk.LabelFrame(parent, text="🛡️ Безопасность", padding=10)
        safety_frame.pack(fill="x", pady=(0, 10))

        self.emergency_stop = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="Экстренная остановка (F12)",
                        variable=self.emergency_stop).pack(anchor="w", pady=2)

        self.mouse_safety = tk.BooleanVar(value=True)
        ttk.Checkbutton(safety_frame, text="Защита от случайных кликов",
                        variable=self.mouse_safety).pack(anchor="w", pady=2)

    def create_scan_settings(self, parent):
        """Настройки сканирования"""
        scan_frame = ttk.LabelFrame(parent, text="🔍 Сканирование", padding=10)
        scan_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(scan_frame, text="Уверенность OCR:").grid(row=0, column=0, sticky="w", pady=2)
        self.confidence = ttk.Scale(scan_frame, from_=0.1, to=1.0, orient="horizontal")
        self.confidence.set(0.8)
        self.confidence.grid(row=0, column=1, sticky="ew", pady=2, padx=(10, 0))

        self.preprocess = tk.BooleanVar(value=True)
        ttk.Checkbutton(scan_frame, text="Пред обработка изображения",
                        variable=self.preprocess).grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

    def create_control_buttons(self, parent):
        """Кнопки управления"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=10)

        # Исправляем вызовы методов
        ttk.Button(button_frame, text="💾 Сохранить",
                   command=self._on_save_clicked).pack(side="right", padx=5)
        ttk.Button(button_frame, text="🔄 Загрузить",
                   command=self._on_load_clicked).pack(side="right", padx=5)

    def _on_save_clicked(self):
        """Обработчик клика по кнопке Сохранить"""
        if self.save_callback:
            self.save_callback()

    def _on_load_clicked(self):
        """Обработчик клика по кнопке Загрузить"""
        if self.load_callback:
            self.load_callback()

    def get_settings(self):
        """Возвращает настройки из GUI"""
        try:
            # Безопасное получение числовых значений
            max_attempts_val = self.max_attempts.get()
            min_delay_val = self.min_delay.get()
            max_delay_val = self.max_delay.get()

            # Проверяем что поля не пустые и конвертируем
            settings = {
                'max_attempts': int(max_attempts_val) if max_attempts_val else 1000,
                'min_delay': float(min_delay_val) if min_delay_val else 0.3,
                'max_delay': float(max_delay_val) if max_delay_val else 0.5,
                'target_mods': [mod.strip() for mod in self.target_mods.get("1.0", "end").split('\n') if mod.strip()],
                'safety': {
                    'emergency_stop': self.emergency_stop.get(),
                    'mouse_safety': self.mouse_safety.get()
                },
                'scanning': {
                    'confidence': self.confidence.get(),
                    'preprocess': self.preprocess.get()
                }
            }
            return settings
        except ValueError as e:
            print(f"❌ Ошибка конвертации значений: {e}")
            # Возвращаем значения по умолчанию при ошибке
            return {
                'max_attempts': 1000,
                'min_delay': 0.3,
                'max_delay': 0.5,
                'click_variance': 15,
                'target_mods': [''],
                'safety': {
                    'emergency_stop': True,
                    'mouse_safety': True
                },
                'scanning': {
                    'confidence': 0.8,
                    'preprocess': True
                }
            }

    def update_from_config(self, config):
        """Обновляет GUI из конфига"""
        try:
            # Основные настройки
            self.max_attempts.delete(0, 'end')
            self.max_attempts.insert(0, str(config.get('max_attempts', 1000)))

            # Целевые моды
            self.target_mods.delete("1.0", "end")
            target_mods = config.get('target_mods', [''])
            self.target_mods.insert("1.0", '\n'.join(target_mods))

            # Настройки задержек
            self.min_delay.delete(0, 'end')
            self.min_delay.insert(0, str(config.get('min_delay', 0.3)))

            self.max_delay.delete(0, 'end')
            self.max_delay.insert(0, str(config.get('max_delay', 0.5)))

            # Безопасность
            safety = config.get('safety', {})
            self.emergency_stop.set(safety.get('emergency_stop', True))
            self.mouse_safety.set(safety.get('mouse_safety', True))

            # Сканирование
            scanning = config.get('scanning', {})
            self.confidence.set(scanning.get('confidence', 0.8))
            self.preprocess.set(scanning.get('preprocess', True))

        except Exception as e:
            print(f"Ошибка обновления настроек: {e}")
