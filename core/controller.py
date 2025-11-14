import pyautogui
import random
import time
from utils.helpers import human_delay, human_click, show_message


class CraftController:
    def __init__(self, safety_manager=None):
        self.safety = safety_manager
        self.action_count = 0

    def use_currency(self, currency_pos, item_pos):
        """Использует валюту на предмете"""
        try:
            # Проверяем безопасность
            if self.safety and not self.safety.check_all_safety_conditions():
                show_message("🚨 Действие отменено по соображениям безопасности")
                return False

            show_message(f"🔄 Использование валюты (попытка #{self.action_count + 1})")

            # Случайный порядок действий (как делает человек)
            if random.random() > 0.7:
                # Сначала предмет, потом валюту
                self._click_item(item_pos)
                human_delay(0.1, 0.3)
                self._click_currency(currency_pos)
            else:
                # Сначала валюту, потом предмет
                self._click_currency(currency_pos)
                human_delay(0.1, 0.3)
                self._click_item(item_pos)

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
