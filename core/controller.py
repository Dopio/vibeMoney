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
            # 2. ПАУЗА чтобы игра обработала взятие валюты
            # 3. ЛЕВАЯ кнопка по предмету (применить)

            # Сначала валюту - ПРАВОЙ кнопкой
            self._click_currency_right(currency_pos)

            # 🔧 ВАЖНАЯ ПАУЗА: ждем пока игра возьмет валюту в руку
            show_message("⏳ Валюту взяли в руку...")
            human_delay(0.4, 0.7)  # Достаточная пауза!

            # Потом предмет - ЛЕВОЙ кнопкой
            self._click_item_left(item_pos)

            # Пауза после всего действия
            human_delay(0.8, 1.5)

            self.action_count += 1

            # Длинная пауза каждые 20 действий
            if self.action_count % 20 == 0:
                show_message("⏸️ Длинная пауза...")
                human_delay(5, 10)

            # Записываем действие
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

        # Простой клик с небольшим смещением
        variance = random.randint(5, 12)
        offset_x = random.randint(-variance, variance)
        offset_y = random.randint(-variance, variance)

        # Двигаемся к цели
        move_duration = random.uniform(0.1, 0.3)
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

        # ПРАВЫЙ клик - берем валюту в руку
        pyautogui.mouseDown(button='right')
        time.sleep(random.uniform(0.1, 0.2))
        pyautogui.mouseUp(button='right')

        # Короткая пауза после клика
        human_delay(0.05, 0.1)

    def _click_item_left(self, item_pos):
        """Клик по предмету ЛЕВОЙ кнопкой мыши (применить валюту)"""
        x, y = item_pos
        show_message(f"🎒 ЛЕВЫЙ клик по предмету: ({x}, {y})")

        # Простой клик с небольшим смещением
        variance = random.randint(3, 8)
        offset_x = random.randint(-variance, variance)
        offset_y = random.randint(-variance, variance)

        # Двигаемся к цели
        move_duration = random.uniform(0.1, 0.25)
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

        # ЛЕВЫЙ клик - применяем валюту на предмет
        pyautogui.mouseDown(button='left')
        time.sleep(random.uniform(0.08, 0.15))
        pyautogui.mouseUp(button='left')

        # Короткая пауза после клика
        human_delay(0.05, 0.1)

    def get_stats(self):
        """Возвращает статистику контроллера"""
        return {
            'total_actions': self.action_count,
            'status': 'active'
        }
