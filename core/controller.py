import pyautogui
import random
import time
from utils.helpers import show_message


class CraftController:
    def __init__(self, safety_manager=None):
        self.safety = safety_manager
        self.action_count = 0
        self.shift_held = False
        self.scanner = None
        self.scan_region = None
        self.min_delay = 0.3
        self.max_delay = 0.5

    def set_scanner(self, scanner):
        """Устанавливает сканер для проверки модов"""
        self.scanner = scanner

    def set_scan_region(self, scan_region):
        """Устанавливает регион сканирования"""
        self.scan_region = scan_region

    def use_currency(self,
                     currency_pos,
                     item_pos,
                     max_attempts=50,
                     target_mods=None,
                     min_delay=0.1,
                     max_delay=0.2):
        """Использует валюту на предмете - ОСНОВНОЙ МЕТОД"""
        try:
            if self.safety and self.safety.check_emergency_stop_requested():
                show_message("🚨 ОСТАНОВКА ПО F12")
                return False

            show_message(f"🔄 Запуск цикла крафта (макс. {max_attempts} попыток)")
            time.sleep(0)

            success = self._use_currency_cycle(currency_pos,
                                               item_pos,
                                               max_attempts,
                                               target_mods,
                                               min_delay,
                                               max_delay)

            if success:
                self.action_count += 1
                if self.safety:
                    self.safety.record_action(success=True, action_type="currency_cycle")

            return success

        except Exception as e:
            show_message(f"❌ Ошибка в цикле крафта: {e}")
            self._release_shift()
            return False

    def _use_currency_cycle(self,
                            currency_pos,
                            item_pos,
                            max_attempts,
                            target_mods,
                            min_delay,
                            max_delay):
        """Цикл крафта - ПКМ на валюту → Shift → ЛКМ на предмет"""
        show_message("⚡ ПКМ + Shift + цикл ЛКМ")

        try:
            # 1. Наводим мышь на валюту
            self._move_to_position(currency_pos, "валюту")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.5)

            # 2. ПРАВАЯ кнопка мыши по валюте
            pyautogui.mouseDown(button='right')
            time.sleep(random.uniform(min_delay, max_delay))
            pyautogui.mouseUp(button='right')
            show_message("💰 Взяли валюту правой кнопкой")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 3. Зажимаем Shift
            pyautogui.keyDown('shift')
            self.shift_held = True
            show_message("⇧ Shift ЗАЖАТ")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 4. Наводим мышь на предмет
            self._move_to_position(item_pos, "предмет")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 5. ЦИКЛ применения валюты
            for attempt in range(1, max_attempts + 1):
                if not self._check_safety_continuous():
                    show_message("🚨 ПРЕРВАНО по F12")
                    self._release_shift()
                    return False

                show_message(f"🎯 Применение #{attempt}")

                # ЛЕВАЯ кнопка мыши по предмету
                pyautogui.mouseDown(button='left')
                time.sleep(random.uniform(min_delay, max_delay))
                pyautogui.mouseUp(button='left')
                show_message(f"✅ Применено {attempt} раз")

                # Обновляем время последнего действия
                if self.safety:
                    self.safety.last_action_time = time.time()

                # Пауза для обновления игры
                show_message("⏳ Жду обновления игры...")
                time.sleep(0.1)

                # Проверяем моды
                if self._check_for_desired_mod(target_mods):
                    show_message(f"🎉 НУЖНЫЙ МОД НАЙДЕН! Попытка: {attempt}")
                    self._release_shift()
                    return True

                # Пауза между применениями
                if attempt < max_attempts:
                    show_message("⏸️ Пауза между применениями...")
                    time.sleep(random.uniform(min_delay, max_delay))

            show_message(f"❌ Цикл завершен - нужный мод не найден за {max_attempts} попыток")
            self._release_shift()
            return False

        except Exception as e:
            self._release_shift()
            raise e

    def _check_for_desired_mod(self, target_mods):
        """Проверяет наличие нужных модов через сканер"""
        if not target_mods or not self.scanner or not self.scan_region:
            return False

        try:
            show_message("🔍 Сканирую моды...")
            mods = self.scanner.scan_item(self.scan_region)

            if mods:
                show_message(f"📄 Найдено модов: {len(mods)}")
                found = self.scanner.has_desired_mod(mods, target_mods)
                return found
            return False

        except Exception as e:
            show_message(f"⚠️ Ошибка проверки модов: {e}")
            return False

    def _check_safety_continuous(self):
        """Проверка безопасности"""
        if not self.safety:
            return True

        if hasattr(self.safety, 'emergency_stop_requested') and self.safety.emergency_stop_requested:
            return False

        return True

    def _release_shift(self):
        """Отпускает Shift если зажат"""
        if self.shift_held:
            pyautogui.keyUp('shift')
            self.shift_held = False
            show_message("⇧ Shift отпущен")

    def _move_to_position(self, position, target_name):
        """Наводим мышь на указанную позицию"""
        x, y = position
        show_message(f"🎯 Наведение на {target_name}: ({x}, {y})")

        variance = random.randint(3, 8)
        offset_x = random.randint(-variance, variance)
        offset_y = random.randint(-variance, variance)

        move_duration = random.uniform(0.2, 0.4)
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

    def stop_crafting(self):
        """Экстренная остановка крафта"""
        self._release_shift()
        show_message("🛑 Крафт принудительно остановлен")

    def get_stats(self):
        """Возвращает статистику контроллера"""
        return {
            'total_actions': self.action_count,
            'shift_held': self.shift_held,
            'status': 'active'
        }
