import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class CalibrationWindow:
    def __init__(self, parent):
        self.save_button = None
        self.cancel_button = None
        self.buttons_frame = None
        self.positions_text = None
        self.progress_bar = None
        self.positions_frame = None
        self.progress_label = None
        self.progress_frame = None
        self.window = None
        self.parent = parent
        self.calibration_data = {}
        self.positions_captured = 0
        self.listener = None

        self.create_window()
        self.setup_listener()

    def create_window(self):
        """Создает окно калибровки"""
        self.window = tk.Toplevel(self.parent.root)
        self.window.title("🎯 Калибровка позиций")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(self.parent.root)
        self.window.grab_set()

        # Центрируем окно
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")

        # Заголовок
        title_label = ttk.Label(self.window,
                                text="Калибровка позиций PoE Craft Bot",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=20)

        # Инструкция
        instruction_text = """
📋 ИНСТРУКЦИЯ ПО КАЛИБРОВКЕ:

1. Нажмите F1 - позиция валюты (Orb of Alteration)
2. Нажмите F2 - позиция предмета для крафта  
3. Нажмите F3 - левый верхний угол области модов
4. Нажмите F4 - правый нижний угол области модов

🎯 Для каждой позиции:
   - Наведите курсор на нужное место
   - Нажмите соответствующую клавишу F1-F4
   - Подтвердите позицию
        """
        instruction_label = ttk.Label(self.window, text=instruction_text,
                                      justify="left", padding=10)
        instruction_label.pack(fill="x", padx=20)

        # Прогресс
        self.progress_frame = ttk.LabelFrame(self.window, text="Прогресс калибровки", padding=10)
        self.progress_frame.pack(fill="x", padx=20, pady=10)

        self.progress_label = ttk.Label(self.progress_frame,
                                        text="Ожидание начала калибровки...",
                                        font=("Arial", 10))
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', maximum=4)
        self.progress_bar.pack(fill="x", pady=5)

        # Текущие позиции
        self.positions_frame = ttk.LabelFrame(self.window, text="Захваченные позиции", padding=10)
        self.positions_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.positions_text = tk.Text(self.positions_frame, height=6, width=50)
        self.positions_text.pack(fill="both", expand=True)
        self.positions_text.insert("1.0", "Позиции появятся здесь...\n")
        self.positions_text.config(state="disabled")

        # Кнопки управления
        self.buttons_frame = ttk.Frame(self.window)
        self.buttons_frame.pack(fill="x", padx=20, pady=10)

        self.cancel_button = ttk.Button(self.buttons_frame, text="❌ Отмена",
                                        command=self.cancel_calibration)
        self.cancel_button.pack(side="left", padx=5)

        self.save_button = ttk.Button(self.buttons_frame, text="💾 Сохранить",
                                      command=self.save_calibration, state="disabled")
        self.save_button.pack(side="right", padx=5)

    def setup_listener(self):
        """Настраивает слушатель горячих клавиш"""
        from pynput import keyboard

        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char in ['1', '2', '3', '4']:
                    # Игнорируем цифры на основной клавиатуре
                    return

                if key == keyboard.Key.f1:
                    self.capture_position('currency_position', "валюты (F1)")
                elif key == keyboard.Key.f2:
                    self.capture_position('item_position', "предмета (F2)")
                elif key == keyboard.Key.f3:
                    self.capture_position('scan_region_start', "начала области модов (F3)")
                elif key == keyboard.Key.f4:
                    self.capture_position('scan_region_end', "конца области модов (F4)")

            except Exception as e:
                print(f"Ошибка в слушателе: {e}")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

        self.update_progress("🎯 Готов к калибровке! Используйте F1-F4")

    def capture_position(self, position_type, description):
        """Захватывает текущую позицию мыши"""
        try:
            import pyautogui
            x, y = pyautogui.position()

            # Подтверждаем захват позиции
            if self.confirm_position(description, x, y):
                self.calibration_data[position_type] = (x, y)
                self.positions_captured += 1

                # Обновляем прогресс
                self.progress_bar['value'] = self.positions_captured
                self.update_positions_display()

                # Проверяем завершение калибровки
                if self.positions_captured >= 4:
                    self.finalize_calibration()
                else:
                    next_step = self.get_next_step()
                    self.update_progress(f"✅ Захвачено: {description}\n➡️ Следующий шаг: {next_step}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось захватить позицию: {e}")

    @classmethod
    def confirm_position(cls, description, x, y):
        """Подтверждает захват позиции"""
        result = messagebox.askyesno(
            "Подтверждение позиции",
            f"Захватить позицию {description}?\nКоординаты: ({x}, {y})\n\n"
            f"Убедитесь что курсор находится над нужным объектом в PoE."
        )
        return result

    def get_next_step(self):
        """Возвращает следующий шаг калибровки"""
        steps = {
            0: "F1 - позиция валюты",
            1: "F2 - позиция предмета",
            2: "F3 - начало области модов",
            3: "F4 - конец области модов"
        }
        return steps.get(self.positions_captured, "Завершено")

    def update_progress(self, message):
        """Обновляет текст прогресса"""
        self.progress_label.config(text=message)

    def update_positions_display(self):
        """Обновляет отображение захваченных позиций"""
        self.positions_text.config(state="normal")
        self.positions_text.delete("1.0", "end")

        positions_info = "📋 ЗАХВАЧЕННЫЕ ПОЗИЦИИ:\n\n"

        for pos_type, coords in self.calibration_data.items():
            if pos_type == 'currency_position':
                positions_info += f"💰 Валюты: {coords}\n"
            elif pos_type == 'item_position':
                positions_info += f"🎒 Предмета: {coords}\n"
            elif pos_type == 'scan_region_start':
                positions_info += f"📏 Начало области: {coords}\n"
            elif pos_type == 'scan_region_end':
                positions_info += f"📏 Конец области: {coords}\n"

        positions_info += f"\n🎯 Прогресс: {self.positions_captured}/4"

        self.positions_text.insert("1.0", positions_info)
        self.positions_text.config(state="disabled")

    def finalize_calibration(self):
        """Завершает калибровку и вычисляет регион сканирования"""
        try:
            # Вычисляем регион сканирования из начальной и конечной точек
            if 'scan_region_start' in self.calibration_data and 'scan_region_end' in self.calibration_data:
                x1, y1 = self.calibration_data['scan_region_start']
                x2, y2 = self.calibration_data['scan_region_end']

                # Вычисляем ширину и высоту
                width = abs(x2 - x1)
                height = abs(y2 - y1)

                # Берем левый верхний угол
                x = min(x1, x2)
                y = min(y1, y2)

                # Сохраняем регион сканирования
                self.calibration_data['scan_region'] = (x, y, width, height)

                # Удаляем временные данные
                del self.calibration_data['scan_region_start']
                del self.calibration_data['scan_region_end']

            self.update_progress("✅ Все позиции захвачены! Сохраняем...")
            self.save_button.config(state="normal")
            self.update_positions_display()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при завершении калибровки: {e}")

    def save_calibration(self):
        """Сохраняет калибровку в конфиг"""
        try:
            # Загружаем существующий конфиг или создаем новый
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Обновляем конфиг новыми позициями
            config.update(self.calibration_data)

            # Сохраняем конфиг
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            # Обновляем родительский конфиг
            self.parent.current_config = config

            messagebox.showinfo("Успех", "Калибровка сохранена! 🎉")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить калибровку: {e}")

    def cancel_calibration(self):
        """Отменяет калибровку"""
        if messagebox.askyesno("Отмена", "Вы уверены что хотите отменить калибровку?"):
            if self.listener:
                self.listener.stop()
            self.window.destroy()
