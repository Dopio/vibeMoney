import pyautogui
import random
import time
from utils.helpers import human_delay, human_click, show_message


class CraftController:
    def __init__(self, safety_manager=None):
        self.safety = safety_manager
        self.action_count = 0

    def use_currency(self, currency_pos, item_pos):
        """Использует валюту на предмете с правильными кнопками мыши"""
        try:
            # Проверяем безопасность
            if self.safety and not self.safety.check_all_safety_conditions():
                show_message("🚨 Действие отменено по соображениям безопасности")
                return False

            show_message(f"🔄 Использование валюты (попытка #{self.action_count + 1})")

            # ПРАВИЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ:
            # 1. ПРАВАЯ кнопка по валюте (взять в руку)
            # 2. ЛЕВАЯ кнопка по предмету (применить)

            # Сначала валюту - ПРАВОЙ кнопкой
            self._click_currency_right(currency_pos)
            human_delay(0.2, 0.5)

            # Потом предмет - ЛЕВОЙ кнопкой
            self._click_item_left(item_pos)

            # Случайная пауза после действия
            human_delay(0.5, 2.0)

            self.action_count += 1

            # Периодически добавляем длинную паузу
            if self.action_count % 20 == 0:
                show_message("⏸️ Длинная пауза...")
                human_delay(5, 10)

            # Записываем действие в систему безопасности
            if self.safety:
                self.safety.record_action(success=True, action_type="currency_use")

            return True

        except Exception as e:
            show_message(f"❌ Ошибка при использовании валюты: {e}")
            if self.safety:
                self.safety.record_action(success=False, action_type="currency_use_error")
            return False

    def _click_currency_right(self, currency_pos):
        """Клик по валюте ПРАВОЙ кнопкой мыши (взять в руку)"""
        x, y = currency_pos
        show_message(f"🖱️ ПРАВЫЙ клик по валюте: ({x}, {y})")

        # Добавляем случайное смещение (5-15 пикселей)
        variance = random.randint(5, 15)
        offset_x = random.randint(-variance, variance)
        offset_y = random.randint(-variance, variance)

        # Случайная скорость движения
        move_duration = random.uniform(0.1, 0.5)

        # Двигаемся к цели
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

        # ПРАВЫЙ клик (взять валюту в руку)
        pyautogui.rightClick()  # Или pyautogui.mouseDown(button='right') + pyautogui.mouseUp(button='right')

        # Случайная микропауза
        human_delay(0.05, 0.2)

    def _click_item_left(self, item_pos):
        """Клик по предмету ЛЕВОЙ кнопкой мыши (применить валюту)"""
        x, y = item_pos
        show_message(f"🎒 ЛЕВЫЙ клик по предмету: ({x}, {y})")

        # Добавляем случайное смещение (3-10 пикселей)
        variance = random.randint(3, 10)
        offset_x = random.randint(-variance, variance)
        offset_y = random.randint(-variance, variance)

        # Случайная скорость движения
        move_duration = random.uniform(0.1, 0.5)

        # Двигаемся к цели
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

        # ЛЕВЫЙ клик (применить валюту на предмет)
        pyautogui.click()  # Стандартный левый клик

        # Случайная микропауза
        human_delay(0.05, 0.2)

    def _click_currency(self, currency_pos):
        """Клик по валюте с человеческой неточностью"""
        x, y = currency_pos
        show_message(f"🖱️ Клик по валюте: ({x}, {y})")

        # Добавляем случайное смещение (5-15 пикселей)
        variance = random.randint(5, 15)
        human_click(x, y, variance)

        # Случайная микропауза
        human_delay(0.05, 0.2)

    def _click_item(self, item_pos):
        """Клик по предмету с человеческой неточностью"""
        x, y = item_pos
        show_message(f"🎒 Клик по предмету: ({x}, {y})")

        # Добавляем случайное смещение (3-10 пикселей)
        variance = random.randint(3, 10)
        human_click(x, y, variance)

    def move_mouse_away(self):
        """Отводим мышь в сторону (естественное поведение)"""
        screen_width, screen_height = pyautogui.size()

        # Случайная позиция в стороне от элементов UI
        safe_x = random.randint(100, screen_width - 100)
        safe_y = random.randint(100, screen_height - 300)  # Избегаем нижней панели

        pyautogui.moveTo(safe_x, safe_y, duration=random.uniform(0.3, 1.0))
        show_message(f"↗️ Перемещение мыши в ({safe_x}, {safe_y})")

    def get_stats(self):
        """Возвращает статистику контроллера"""
        return {
            'total_actions': self.action_count,
            'status': 'active'
        }
