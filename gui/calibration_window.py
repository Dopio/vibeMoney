import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import json
import time
import threading
import os
from datetime import datetime
from pynput import keyboard


class CalibrationWindow:
    def __init__(self, parent_gui):  # ИЗМЕНИТЕ ПАРАМЕТР
        self.parent_gui = parent_gui  # Сохраняем ссылку на основной GUI
        self.window = tk.Toplevel(parent_gui.root)  # Используем root из parent_gui
        self.window.title("Калибровка PoE Craft Bot")
        self.window.geometry("600x500")
        self.window.focus_force()

        self.steps = [
            {"name": "Orb of Alteration", "key": "F1", "config_key": "currency_position"},
            {"name": "Предмет для крафта", "key": "F2", "config_key": "item_position"},
            {"name": "Левый верхний угол текста модов", "key": "F3", "config_key": "scan_start"},
            {"name": "Правый нижний угол текста модов", "key": "F4", "config_key": "scan_end"}
        ]
        self.current_step = 0
        self.positions = {}
        self.keyboard_listener = None

        self.create_widgets()
        self.start_keyboard_listener()
        self.update_coordinates()

    def create_widgets(self):
        # Заголовок
        title = ttk.Label(self.window, text="🎯 Калибровка позиций",
                          font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Инструкция
        instruction = ttk.Label(self.window,
                                text="Используйте горячие клавиши для калибровки:\nНе нужно нажимать кнопки в этом окне!",
                                justify="center", foreground="blue")
        instruction.pack(pady=5)

        # Текущий шаг
        self.step_frame = ttk.LabelFrame(self.window, text="Текущий шаг")
        self.step_frame.pack(fill="x", padx=10, pady=5)

        self.step_label = ttk.Label(self.step_frame, text="", font=("Arial", 11))
        self.step_label.pack(pady=10)

        # Прогресс
        self.progress_frame = ttk.LabelFrame(self.window, text="Прогресс")
        self.progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate',
                                            maximum=len(self.steps))
        self.progress_bar.pack(fill="x", padx=10, pady=5)

        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(pady=5)

        # Координаты в реальном времени
        self.coord_frame = ttk.LabelFrame(self.window, text="Координаты мыши")
        self.coord_frame.pack(fill="x", padx=10, pady=5)

        self.coord_label = ttk.Label(self.coord_frame, text="Двигайте мышь...",
                                     font=("Arial", 10))
        self.coord_label.pack(pady=10)

        # Захваченные позиции
        self.preview_frame = ttk.LabelFrame(self.window, text="Захваченные позиции")
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_text = tk.Text(self.preview_frame, height=8, width=60)
        self.preview_text.pack(pady=5, padx=10, fill="both", expand=True)

        # Кнопки управления
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="❌ Отмена",
                   command=self.cancel_calibration).pack(side="left", padx=5)

        self.save_btn = ttk.Button(btn_frame, text="💾 Сохранить",
                                   command=self.save_calibration, state="disabled")
        self.save_btn.pack(side="left", padx=5)

        # Кнопка принудительного сохранения
        self.force_save_btn = ttk.Button(btn_frame, text="🚀 Сохранить сейчас",
                                         command=self.force_save, state="normal")
        self.force_save_btn.pack(side="left", padx=5)

        self.update_step_display()

    def start_keyboard_listener(self):
        """Запускает отслеживание горячих клавиш"""

        def on_press(key):
            try:
                if key == keyboard.Key.f1 and self.current_step == 0:
                    self.capture_position("F1")
                elif key == keyboard.Key.f2 and self.current_step == 1:
                    self.capture_position("F2")
                elif key == keyboard.Key.f3 and self.current_step == 2:
                    self.capture_position("F3")
                elif key == keyboard.Key.f4 and self.current_step == 3:
                    self.capture_position("F4")
            except:
                pass

        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def capture_position(self, key_pressed):
        """Захватывает текущую позицию мыши по горячей клавише"""
        x, y = pyautogui.position()

        # Находим текущий шаг по нажатой клавише
        for i, step in enumerate(self.steps):
            if step["key"] == key_pressed and i == self.current_step:
                self.positions[step["config_key"]] = (x, y)

                # Добавляем визуальную обратную связь
                self.show_capture_feedback(x, y, step["name"])

                # АВТОСОХРАНЕНИЕ после каждого шага
                self.auto_save_config()

                # Переходим к следующему шагу
                self.current_step += 1
                self.update_step_display()
                break

    def show_capture_feedback(self, x, y, step_name):
        """Показывает подтверждение захвата"""
        feedback_text = f"✅ {step_name}: ({x}, {y})"

        self.preview_text.insert(tk.END, feedback_text + "\n")
        self.preview_text.see(tk.END)

        # Мигание для обратной связи
        self.coord_label.config(text=f"✅ ЗАХВАЧЕНО: ({x}, {y})", foreground="green")
        self.window.after(1000, lambda: self.coord_label.config(foreground="black"))

    def auto_save_config(self):
        """Автоматически сохраняет конфиг после каждого шага"""
        try:
            temp_config = self.prepare_config()

            # СОХРАНЯЕМ В ОСНОВНОЙ КОНФИГ, А НЕ ВО ВРЕМЕННЫЙ!
            with open('config.json', 'w') as f:  # ИЗМЕНИТЕ config_temp.json на config.json
                json.dump(temp_config, f, indent=4)

            # Логируем в основной лог
            self.log_calibration_step(temp_config)

            print(f"💾 Автосохранение в config.json: {len(self.positions)}/4 позиций")

        except Exception as e:
            print(f"⚠️ Ошибка автосохранения: {e}")

    def log_calibration_step(self, config):
        """Логирует шаг калибровки в основной лог"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event': 'calibration_step',
                'step': self.current_step,
                'positions_captured': len(self.positions),
                'config_preview': {
                    'currency_position': config.get('currency_position'),
                    'item_position': config.get('item_position'),
                    'scan_region': config.get('scan_region', 'Неполный'),
                    'target_mods': config.get('target_mods', [])
                }
            }

            # Записываем в лог-файл
            with open('calibration_log.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

            # Также выводим в консоль
            print(f"📝 Лог: шаг {self.current_step}, позиций: {len(self.positions)}")

        except Exception as e:
            print(f"⚠️ Ошибка логирования: {e}")

    def prepare_config(self):
        """Подготавливает конфиг для сохранения"""
        config = self.positions.copy()

        # Формируем область сканирования если есть обе точки
        if 'scan_start' in config and 'scan_end' in config:
            x1, y1 = config['scan_start']
            x2, y2 = config['scan_end']
            config['scan_region'] = (
                min(x1, x2), min(y1, y2),
                abs(x2 - x1), abs(y2 - y1)
            )
            # УДАЛЯЕМ ВРЕМЕННЫЕ КЛЮЧИ
            del config['scan_start']
            del config['scan_end']

        # Добавляем настройки по умололчанию
        config['target_mods'] = ["increased", "damage", "critical", "speed"]
        config['max_attempts'] = 200
        config['min_delay'] = 0.5
        config['max_delay'] = 2.0
        config['calibration_time'] = datetime.now().isoformat()

        return config

    def update_step_display(self):
        """Обновляет отображение текущего шага"""
        if self.current_step < len(self.steps):
            current_step_info = self.steps[self.current_step]
            step_text = f"{current_step_info['name']}\nНажмите {current_step_info['key']} для захвата позиции"
            self.step_label.config(text=step_text)

            # Обновляем прогресс
            self.progress_bar['value'] = self.current_step
            self.progress_label.config(text=f"Шаг {self.current_step + 1} из {len(self.steps)}")

        else:
            # Все шаги завершены
            self.step_label.config(text="✅ Все позиции захвачены!\nМожно сохранять конфигурацию.")
            self.progress_bar['value'] = len(self.steps)
            self.progress_label.config(text="Готово!")

            # ВКЛЮЧАЕМ КНОПКУ СОХРАНЕНИЯ ТОЛЬКО ЕСЛИ ВСЕ 4 ПОЗИЦИИ ЗАХВАЧЕНЫ
            required_keys = ['currency_position', 'item_position', 'scan_start', 'scan_end']
            if all(key in self.positions for key in required_keys):
                self.save_btn.config(state="normal")
            else:
                self.step_label.config(text="❌ Не все позиции захвачены!\nПроверьте F1-F4")

    def update_coordinates(self):
        """Обновляет координаты мыши в реальном времени"""
        try:
            x, y = pyautogui.position()
            self.coord_label.config(text=f"X: {x}, Y: {y}")
        except:
            pass

        # Продолжаем обновление если окно открыто
        if self.window.winfo_exists():
            self.window.after(100, self.update_coordinates)

    def force_save(self):
        """Принудительное сохранение текущего состояния"""
        try:
            config = self.prepare_config()

            # ПРОВЕРЯЕМ ЧТО ВСЕ ОСНОВНЫЕ ПОЗИЦИИ ЕСТЬ
            required_positions = ['currency_position', 'item_position']
            missing_positions = [pos for pos in required_positions if pos not in config]

            if missing_positions:
                messagebox.showwarning("Внимание",
                                       f"Отсутствуют позиции: {', '.join(missing_positions)}\n"
                                       f"Конфиг может быть неполным.")

            # Сохраняем основной конфиг
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            # ОБНОВЛЯЕМ ОСНОВНОЙ GUI
            if hasattr(self.parent_gui, 'load_config'):
                self.parent_gui.load_config()
                self.parent_gui.log_message("✅ Конфиг сохранен принудительно")

            messagebox.showinfo("Успех",
                                f"Конфиг сохранен принудительно!\n"
                                f"Захвачено позиций: {len(self.positions)}/4\n"
                                f"Файл: config.json")

            print("💾 Принудительное сохранение выполнено")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def save_calibration(self):
        """Сохраняет калибровку"""
        try:
            config = self.prepare_config()

            print("💾 Сохраняю конфиг в config.json...")
            print(f"   Валюты: {config.get('currency_position')}")
            print(f"   Предмет: {config.get('item_position')}")

            # Сохраняем в ОСНОВНОЙ файл
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

            print("✅ Конфиг сохранен в config.json")

            # УБЕРИТЕ удаление временного файла или закомментируйте:
            # if os.path.exists('config_temp.json'):
            #     os.remove('config_temp.json')

            # Закрываем окно
            if self.keyboard_listener:
                self.keyboard_listener.stop()

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def cancel_calibration(self):
        """Отменяет калибровку"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.window.destroy()
