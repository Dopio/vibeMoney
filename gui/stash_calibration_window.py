import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pynput import keyboard
import pyautogui


class StashCalibrationWindow:
    def __init__(self, parent):
        self.parent = parent
        self.calibration_data = {}
        self.positions_captured = 0
        self.listener = None

        self.window = None
        self.save_button = None
        self.cancel_button = None
        self.positions_text = None
        self.progress_bar = None
        self.progress_label = None

        self.create_window()
        self.setup_listener()

    def create_window(self):
        """Создает окно калибровки вкладки"""
        self.window = tk.Toplevel(self.parent.root)
        self.window.title("📦 Калибровка вкладки стима")
        self.window.geometry("500x450")
        self.window.resizable(False, False)
        self.window.transient(self.parent.root)
        self.window.grab_set()

        # Центрируем окно
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (450 // 2)
        self.window.geometry(f"500x450+{x}+{y}")

        # Заголовок
        title_label = ttk.Label(self.window,
                                text="Калибровка вкладки для массового крафта",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=20)

        # Инструкция
        instruction_text = """
        📋 ИНСТРУКЦИЯ ПО КАЛИБРОВКЕ ВКЛАДКИ:

        1. Нажмите F1 - позиция вкладки
        2. Нажмите F2 - левый верхний угол области предметов  
        3. Нажмите F3 - правый нижний угол области предметов
        4. Нажмите F4 - левый верхний предмет в сетке 

        🎯 Размер сетки: 6 предметов в ряд × 3 ряда = 18 предметов

        💡 Позиции захватываются автоматически без подтверждения!
           Данные сохранятся после 4-го шага.
        """
        instruction_label = ttk.Label(self.window, text=instruction_text,
                                      justify="left", padding=10)
        instruction_label.pack(fill="x", padx=20)

        # Прогресс
        progress_frame = ttk.LabelFrame(self.window, text="Прогресс калибровки", padding=10)
        progress_frame.pack(fill="x", padx=20, pady=10)

        self.progress_label = ttk.Label(progress_frame,
                                        text="Ожидание начала калибровки...",
                                        font=("Arial", 10))
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', maximum=4)
        self.progress_bar.pack(fill="x", pady=5)

        # Текущие позиции
        positions_frame = ttk.LabelFrame(self.window, text="Захваченные позиции", padding=10)
        positions_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.positions_text = tk.Text(positions_frame, height=7, width=50)
        self.positions_text.pack(fill="both", expand=True)
        self.positions_text.insert("1.0", "Позиции появятся здесь...\n")
        self.positions_text.config(state="disabled")

        # Кнопки управления
        buttons_frame = ttk.Frame(self.window)
        buttons_frame.pack(fill="x", padx=20, pady=10)

        self.cancel_button = ttk.Button(buttons_frame, text="❌ Отмена",
                                        command=self.cancel_calibration)
        self.cancel_button.pack(side="left", padx=5)

        self.save_button = ttk.Button(buttons_frame, text="💾 Сохранить",
                                      command=self.save_calibration, state="disabled")
        self.save_button.pack(side="right", padx=5)

    def setup_listener(self):
        """Настраивает слушатель горячих клавиш"""

        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char in ['1', '2', '3', '4']:
                    return

                if key == keyboard.Key.f1:
                    self.capture_position('stash_tab_position', "вкладки стима (F1)")
                elif key == keyboard.Key.f2:
                    self.capture_position('item_area_start', "начала области предметов (F2)")
                elif key == keyboard.Key.f3:
                    self.capture_position('item_area_end', "конца области предметов (F3)")
                elif key == keyboard.Key.f4:
                    self.capture_position('first_item_position', "первого предмета (F4)")

            except Exception as e:
                print(f"Ошибка в слушателе: {e}")

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.daemon = True
        self.listener.start()

        self.update_progress("🎯 Готов к калибровке вкладки! Используйте F1-F4")

    def capture_position(self, position_type, description):
        """Захватывает текущую позицию мыши БЕЗ подтверждения"""
        try:
            x, y = pyautogui.position()

            # ЗАХВАТЫВАЕМ ПОЗИЦИЮ БЕЗ ПОДТВЕРЖДЕНИЯ
            self.calibration_data[position_type] = (x, y)
            self.positions_captured += 1

            self.progress_bar['value'] = self.positions_captured
            self.update_positions_display()

            # Обновляем прогресс
            self.update_progress(f"✅ Захвачено: {description}")

            # Проверяем завершение калибровки
            if self.positions_captured >= 4:
                self.finalize_calibration()
            else:
                next_step = self.get_next_step()
                self.update_progress(f"✅ Захвачено: {description}\n➡️ Следующий шаг: {next_step}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось захватить позицию: {e}")

    def get_next_step(self):
        """Возвращает следующий шаг калибровки"""
        steps = {
            0: "F1 - позиция вкладки",
            1: "F2 - начало области предметов",
            2: "F3 - конец области предметов",
            3: "F4 - первый предмет в сетке"
        }
        return steps.get(self.positions_captured, "Завершено")

    def update_progress(self, message):
        """Обновляет текст прогресса"""
        self.progress_label.config(text=message)

    def update_positions_display(self):
        """Обновляет отображение захваченных позиций"""
        self.positions_text.config(state="normal")
        self.positions_text.delete("1.0", "end")

        positions_info = "📋 ЗАХВАЧЕННЫЕ ПОЗИЦИИ ВКЛАДКИ:\n\n"

        for pos_type, coords in self.calibration_data.items():
            if pos_type == 'stash_tab_position':
                positions_info += f"📦 Вкладка: {coords}\n"
            elif pos_type == 'item_area_start':
                positions_info += f"📏 Начало области: {coords}\n"
            elif pos_type == 'item_area_end':
                positions_info += f"📏 Конец области: {coords}\n"
            elif pos_type == 'first_item_position':
                positions_info += f"🎯 Первый предмет: {coords}\n"

        positions_info += f"\n🎯 Прогресс: {self.positions_captured}/4"

        # Показываем следующий шаг
        if self.positions_captured < 4:
            next_step = self.get_next_step()
            positions_info += f"\n➡️ Следующий шаг: {next_step}"

        self.positions_text.insert("1.0", positions_info)
        self.positions_text.config(state="disabled")

    def finalize_calibration(self):
        """Завершает калибровку и автоматически сохраняет"""
        try:
            # Вычисляем регион предметов
            if 'item_area_start' in self.calibration_data and 'item_area_end' in self.calibration_data:
                x1, y1 = self.calibration_data['item_area_start']
                x2, y2 = self.calibration_data['item_area_end']

                width = abs(x2 - x1)
                height = abs(y2 - y1)
                x = min(x1, x2)
                y = min(y1, y2)

                self.calibration_data['item_area_region'] = (x, y, width, height)
                del self.calibration_data['item_area_start']
                del self.calibration_data['item_area_end']

            # ВЫЧИСЛЯЕМ СЕТКУ С ПРАВИЛЬНЫМИ ШАГАМИ
            if 'first_item_position' in self.calibration_data and 'item_area_region' in self.calibration_data:
                first_x, first_y = self.calibration_data['first_item_position']
                area_x, area_y, area_width, area_height = self.calibration_data['item_area_region']

                # Используем метод с правильными шагами 100x198
                item_slots = self.calculate_item_grid_precise(
                    first_x, first_y,
                    area_x, area_y, area_width, area_height,
                    grid_columns=6, grid_rows=3
                )

                self.calibration_data['item_slots'] = item_slots

            self.update_progress("✅ Все позиции захвачены! Сохраняем...")

            # АВТОМАТИЧЕСКИ СОХРАНЯЕМ
            self.save_calibration()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при завершении калибровки: {e}")

    def calculate_item_grid_precise(self, first_x, first_y, area_x, area_y, area_width, area_height, grid_columns=6,
                                    grid_rows=3):
        """
        Точное вычисление сетки на основе реальных расстояний между предметами
        """
        item_slots = []

        # РЕАЛЬНЫЕ РАССТОЯНИЯ ИЗ ВАШИХ КООРДИНАТ
        step_x = 100  # Расстояние между предметами по X
        step_y = 198  # Расстояние между предметами по Y

        # Создаем сетку 6x3 начиная с откалиброванной первой позиции
        for row in range(grid_rows):
            for col in range(grid_columns):
                slot_x = first_x + (col * step_x)
                slot_y = first_y + (row * step_y)
                item_slots.append([int(slot_x), int(slot_y)])

        return item_slots

    def save_calibration(self):
        """Сохраняет калибровку в конфиг и закрывает окно"""
        try:
            # Загружаем существующий конфиг
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}

            # Обновляем конфиг данными вкладки
            config.update(self.calibration_data)

            # Добавляем timestamp
            from datetime import datetime
            config['stash_calibration_time'] = datetime.now().isoformat()

            # Сохраняем конфиг
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            # Обновляем родительский конфиг
            self.parent.current_config = config

            messagebox.showinfo("Успех",
                                "Калибровка вкладки сохранена! 🎉\n\nДанные автоматически записаны в config.json")

            # АВТОМАТИЧЕСКИ ЗАКРЫВАЕМ ОКНО ПОСЛЕ СОХРАНЕНИЯ
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить калибровку: {e}")

    def cancel_calibration(self):
        """Отменяет калибровку"""
        if messagebox.askyesno("Отмена", "Вы уверены что хотите отменить калибровку вкладки?"):
            if self.listener:
                self.listener.stop()
            self.window.destroy()
