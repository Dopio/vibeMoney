import pyautogui
import random
import time
from utils.helpers import human_delay, show_message


class CraftController:
    def __init__(self, safety_manager=None):
        self.safety = safety_manager
        self.action_count = 0
        self.shift_held = False
        self.scanner = None
        self.scan_region = None

    def set_scanner(self, scanner):
        """Устанавливает сканер для проверки модов"""
        self.scanner = scanner

    def set_scan_region(self, scan_region):
        """Устанавливает регион сканирования"""
        self.scan_region = scan_region

    def use_currency(self, currency_pos, item_pos, max_attempts=50, target_mods=None):
        """Использует валюту на предмете с проверкой F12 и модов"""
        try:
            # НЕМЕДЛЕННАЯ проверка F12
            if self.safety and self.safety.check_emergency_stop_requested():
                show_message("🚨 ОСТАНОВКА ПО F12 - операция отменена")
                return False

            show_message(f"🔄 Запуск цикла крафта (макс. {max_attempts} попыток)")
            show_message("🎯 Для экстренной остановки нажмите F12")

            # 🔧 ДОБАВЛЯЕМ ПАУЗУ ПЕРЕД НАЧАЛОМ
            time.sleep(1)

            # Запускаем цикл крафта
            success = self._use_currency_cycle(currency_pos, item_pos, max_attempts, target_mods)

            if success:
                self.action_count += 1
                if self.safety:
                    self.safety.record_action(success=True, action_type="currency_cycle")

            return success

        except Exception as e:
            show_message(f"❌ Ошибка в цикле крафта: {e}")
            self._release_shift()
            return False

    def _use_currency_cycle(self, currency_pos, item_pos, max_attempts, target_mods):
        """Цикл крафта с ПРАВИЛЬНОЙ обработкой безопасности"""
        show_message("⚡ ПКМ + Shift + цикл ЛКМ")

        try:
            # 🔧 СНАЧАЛА ПРОВЕРЯЕМ ТЕКУЩИЕ МОДЫ
            show_message("🔍 Первоначальное сканирование модов...")
            initial_mods = self._scan_current_mods(target_mods)
            if initial_mods and self._check_mods_for_target(initial_mods, target_mods):
                show_message("⚠️ Целевой мод уже есть на предмете!")
                return False

            # 1. Наводим мышь на валюту
            self._move_to_position(currency_pos, "валюту")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.5)

            # 2. ПРАВАЯ кнопка мыши по валюте
            pyautogui.mouseDown(button='right')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='right')
            show_message("💰 Взяли валюту правой кнопкой")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.5)

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

            # 🔧 ЗАПИСЫВАЕМ ОДНО ДЕЙСТВИЕ ДЛЯ ВСЕГО ЦИКЛА
            if self.safety:
                self.safety.record_action(success=True, action_type="currency_cycle_start")

            # 5. ЦИКЛ: применяем валюту и проверяем моды
            for attempt in range(1, max_attempts + 1):
                # ✅ Проверяем F12
                if not self._check_safety_continuous():
                    show_message("🚨 ПРЕРВАНО по F12")
                    self._release_shift()
                    return False

                show_message(f"🎯 Применение #{attempt}")

                # ЛЕВАЯ кнопка мыши по предмету
                pyautogui.mouseDown(button='left')
                time.sleep(random.uniform(0.1, 0.2))
                pyautogui.mouseUp(button='left')

                show_message(f"✅ Применено {attempt} раз")

                # 🔧 НЕ ЗАПИСЫВАЕМ КАЖДЫЙ КЛИК - только обновляем время
                if self.safety:
                    # Просто обновляем время без записи в лог
                    self.safety.last_action_time = time.time()

                # 🔧 ПАУЗА ДЛЯ ОБНОВЛЕНИЯ ИГРЫ
                show_message("⏳ Жду обновления игры...")
                time.sleep(1.5)

                # 🔧 ПРОВЕРЯЕМ МОДЫ ПОСЛЕ применения валюты
                show_message("🔍 Сканирую новые моды...")
                current_mods = self._scan_current_mods(target_mods)

                if current_mods:
                    show_message(f"📄 Найдено модов: {len(current_mods)}")
                    # Логируем все найденные моды
                    for i, mod in enumerate(current_mods, 1):
                        show_message(f"   {i}. {mod}")

                    # 🔧 ПРОВЕРЯЕМ НАЛИЧИЕ ЦЕЛЕВЫХ МОДОВ
                    if self._check_mods_for_target(current_mods, target_mods):
                        show_message(f"🎉 НУЖНЫЙ МОД НАЙДЕН! Попытка: {attempt}")
                        self._release_shift()
                        # 🔧 ЗАПИСЫВАЕМ УСПЕШНОЕ ЗАВЕРШЕНИЕ
                        if self.safety:
                            self.safety.record_action(success=True, action_type="currency_cycle_success")
                        return True
                    else:
                        show_message("❌ Целевые моды не найдены, продолжаем...")
                else:
                    show_message("❌ Не удалось распознать моды, продолжаем...")

                # 🔧 ПАУЗА МЕЖДУ ПРИМЕНЕНИЯМИ БЕЗ ЗАПИСИ ДЕЙСТВИЙ
                if attempt < max_attempts:
                    show_message("⏸️ Пауза между применениями...")
                    # Простая пауза без проверки безопасности (она уже в цикле)
                    time.sleep(random.uniform(0.5, 1.0))

            # Если дошли сюда - не нашли нужный мод
            show_message(f"❌ Цикл завершен - нужный мод не найден за {max_attempts} попыток")
            self._release_shift()
            # 🔧 ЗАПИСЫВАЕМ НЕУДАЧНОЕ ЗАВЕРШЕНИЕ
            if self.safety:
                self.safety.record_action(success=False, action_type="currency_cycle_failed")
            return False

        except Exception as e:
            self._release_shift()
            if self.safety:
                self.safety.record_action(success=False, action_type="currency_cycle_error")
            raise e

    def _check_for_desired_mod(self, target_mods):
        """РЕАЛЬНАЯ проверка модов через сканер"""
        if not target_mods or not self.scanner or not self.scan_region:
            show_message("⚠️ Не настроен сканер или регион сканирования")
            return False

        try:
            show_message("🔍 Сканирую моды...")
            mods = self.scanner.scan_item(self.scan_region)

            if mods:
                show_message(f"📄 Найдено модов: {len(mods)}")
                # Логируем все найденные моды
                for i, mod in enumerate(mods, 1):
                    show_message(f"   {i}. {mod}")

                # Проверяем целевые моды
                found = self.scanner.has_desired_mod(mods, target_mods)
                if found:
                    show_message(f"🎯 Найден целевой мод: {target_mods}")
                    return True
                else:
                    show_message("❌ Целевые моды не найдены")
            else:
                show_message("❌ Не удалось распознать моды")

            return False

        except Exception as e:
            show_message(f"⚠️ Ошибка проверки модов: {e}")
            return False

    def _scan_current_mods(self, target_mods):
        """Сканирует текущие моды предмета"""
        if not target_mods or not self.scanner or not self.scan_region:
            return []

        try:
            # 🔧 ОЧИЩАЕМ КЭШ СКАНЕРА ПЕРЕД КАЖДЫМ СКАНИРОВАНИЕМ
            if hasattr(self.scanner, 'last_scan_hash'):
                self.scanner.last_scan_hash = None
            if hasattr(self.scanner, 'last_scan_result'):
                self.scanner.last_scan_result = None

            mods = self.scanner.scan_item(self.scan_region)
            return mods if mods else []

        except Exception as e:
            show_message(f"⚠️ Ошибка сканирования модов: {e}")
            return []

    def _check_mods_for_target(self, mods, target_mods):
        """Проверяет, есть ли целевые моды в списке"""
        if not mods or not target_mods:
            return False

        try:
            found = self.scanner.has_desired_mod(mods, target_mods)
            return found
        except Exception as e:
            show_message(f"⚠️ Ошибка проверки модов: {e}")
            return False

    def _check_safety_continuous(self):
        """Упрощенная проверка безопасности"""
        if not self.safety:
            return True

        # 🔧 ИСПРАВЛЕНИЕ: правильная проверка F12
        if (hasattr(self.safety, 'emergency_stop_requested') and self.safety.emergency_stop_requested):
            return False

        return True

    def _safe_delay(self, min_seconds, max_seconds):
        """Упрощенная задержка"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
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
