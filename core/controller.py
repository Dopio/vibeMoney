import pyautogui
import random
import time
import threading
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

        # Новые поля для массового крафта
        self.is_mass_crafting = False
        self.current_item_index = 0
        self.successful_crafts = []
        self.item_slots = []
        self.mass_craft_thread = None
        self.stash_tab_position = None

    def set_scanner(self, scanner):
        """Устанавливает сканер для проверки модов"""
        self.scanner = scanner

    def set_scan_region(self, scan_region):
        """Устанавливает регион сканирования"""
        self.scan_region = scan_region

    def set_item_slots(self, item_slots):
        """Устанавливает слоты предметов для массового крафта"""
        self.item_slots = item_slots
        show_message(f"📦 Загружено {len(item_slots)} слотов предметов")

    def set_stash_tab_position(self, position):
        """Устанавливает позицию вкладки stash"""
        self.stash_tab_position = position
        show_message(f"📁 Позиция вкладки установлена: {position}")

    def start_mass_craft(self, currency_pos, target_mods, max_attempts_per_item=50):
        """Запускает массовый крафт для всех предметов в сетке"""
        if self.is_mass_crafting:
            show_message("⚠️ Массовый крафт уже запущен")
            return False

        if not self.item_slots:
            show_message("❌ Нет загруженных слотов предметов")
            return False

        if not currency_pos:
            show_message("❌ Не указана позиция валюты")
            return False

        if not self.stash_tab_position:
            show_message("❌ Не указана позиция вкладки stash")
            return False

        show_message(f"🚀 Запуск массового крафта для {len(self.item_slots)} предметов")

        self.is_mass_crafting = True
        self.current_item_index = 0
        self.successful_crafts = []

        # Запускаем в отдельном потоке
        self.mass_craft_thread = threading.Thread(
            target=self._mass_craft_worker,
            args=(currency_pos, target_mods, max_attempts_per_item),
            daemon=True
        )
        self.mass_craft_thread.start()

        return True

    def _mass_craft_worker(self, currency_pos, target_mods, max_attempts_per_item):
        """Рабочий процесс массового крафта"""
        try:
            total_items = len(self.item_slots)

            for item_index, item_pos in enumerate(self.item_slots):
                # ✅ ПРОВЕРКА F12 ПЕРЕД КАЖДЫМ ПРЕДМЕТОМ
                if not self.is_mass_crafting or (self.safety and self.safety.check_emergency_stop_requested()):
                    show_message("🚨 Прервано по F12")
                    break

                self.current_item_index = item_index
                show_message(f"🔧 Обработка предмета {item_index + 1}/{total_items}")

                # Крафтим один предмет
                success = self._craft_single_item(
                    currency_pos,
                    item_pos,
                    target_mods,
                    max_attempts_per_item
                )

                if success:
                    self.successful_crafts.append({
                        'item_index': item_index,
                        'position': item_pos,
                        'timestamp': time.time()
                    })
                    show_message(f"✅ Предмет {item_index + 1} успешно прокрафтен!")
                else:
                    # ✅ ПРОВЕРЯЕМ F12 ПРИ НЕУДАЧЕ
                    if self.safety and self.safety.check_emergency_stop_requested():
                        show_message("🚨 Прервано по F12")
                        break
                    show_message(f"❌ Предмет {item_index + 1} не удалось прокрафтить")

            # Завершение массового крафта
            self.is_mass_crafting = False
            success_count = len(self.successful_crafts)
            show_message(f"🎉 Массовый крафт завершен! Успешно: {success_count}/{total_items}")

        except Exception as e:
            self.is_mass_crafting = False
            show_message(f"❌ Ошибка в массовом крафте: {e}")

    def _craft_single_item(self, currency_pos, item_pos, target_mods, max_attempts):
        """Крафт одного предмета до получения нужного мода"""
        try:
            # 1. Правый клик по валюте
            self._log_important("💰 Правый клик по валюте")
            self._move_to_position_silent(currency_pos)
            if not self._check_safety_continuous():
                return False

            pyautogui.mouseDown(button='right')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='right')
            time.sleep(0.3)

            # 2. Зажимаем Shift
            self._log_important("⇧ Зажимаем Shift")
            pyautogui.keyDown('shift')
            self.shift_held = True
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 3. Перемещаемся на вкладку stash
            self._log_important("📁 Переходим на вкладку stash")
            self._move_to_position_silent(self.stash_tab_position)
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 4. Левый клик по вкладке (переходим на нее)
            self._log_important("👆 Левый клик по вкладке")
            pyautogui.mouseDown(button='left')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='left')
            time.sleep(0.5)  # Ждем перехода на вкладку

            # 5. Наводимся на предмет
            self._log_important(f"🎯 Наводимся на предмет {self.current_item_index + 1}")
            self._move_to_position_silent(item_pos)
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 6. Цикл крафта для этого предмета
            success = self._craft_item_cycle(target_mods, max_attempts, item_pos)

            self._release_shift()
            return success

        except Exception as e:
            self._release_shift()
            show_message(f"❌ Ошибка крафта предмета: {e}")
            return False

    def _craft_item_cycle(self, target_mods, max_attempts, item_pos):
        """Цикл крафта для одного предмета"""
        self._log_important("⚡ Начинаем цикл крафта предмета...")

        # Вычисляем область сканирования для этого предмета
        mods_region = self.scanner.get_mods_region_for_item(item_pos[0], item_pos[1])

        for attempt in range(1, max_attempts + 1):
            if not self._check_safety_continuous():
                self._log_important("🚨 Прервано по F12")
                return False

            # Левый клик по предмету (применяем валюту)
            pyautogui.mouseDown(button='left')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='left')

            # Обновляем время последнего действия
            if self.safety:
                self.safety.last_action_time = time.time()

            # Пауза для обновления игры
            time.sleep(0.3)

            # Проверяем моды
            if attempt % 5 == 0 or attempt == max_attempts:
                self._log_important(f"🔍 Проверка модов (попытка {attempt})")

            if self._check_for_desired_mod(target_mods, mods_region):
                self._log_important(f"🎉 Нужный мод найден! Попытка: {attempt}")
                return True

            # Пауза между применениями
            if attempt < max_attempts:
                time.sleep(random.uniform(0.1, 0.2))

        self._log_important(f"❌ Целевой мод не найден за {max_attempts} попыток")
        return False

    def use_currency(self,
                     currency_pos,
                     item_pos,
                     max_attempts=50,
                     target_mods=None,
                     min_delay=0.1,
                     max_delay=0.2):
        """Использует валюту на предмете - ОСНОВНОЙ МЕТОД (совместимость)"""
        try:
            if self.safety and self.safety.check_emergency_stop_requested():
                show_message("🚨 ОСТАНОВКА ПО F12")
                return False

            show_message(f"🔄 Запуск цикла крафта (макс. {max_attempts} попыток)")

            success = self._use_currency_cycle(currency_pos,
                                               item_pos,
                                               max_attempts,
                                               target_mods,
                                               min_delay,
                                               max_delay,
                                               self.scan_region)

            if success:
                self.action_count += 1
                if self.safety:
                    self.safety.record_action(success=True, action_type="currency_cycle")

            return success

        except Exception as e:
            show_message(f"❌ Ошибка в цикле крафта: {e}")
            self._release_shift()
            return False

    def _use_currency_cycle(self, currency_pos, item_pos, max_attempts, target_mods, min_delay, max_delay,
                            mods_region=None):
        """Цикл крафта для обычного режима (без вкладки)"""
        self._log_important("⚡ Начинаем цикл крафта...")

        try:
            # 1. Наводим мышь на валюту
            self._move_to_position_silent(currency_pos)
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.5)

            # 2. ПРАВАЯ кнопка мыши по валюте
            pyautogui.mouseDown(button='right')
            time.sleep(random.uniform(min_delay, max_delay))
            pyautogui.mouseUp(button='right')
            time.sleep(0.3)

            # 3. Зажимаем Shift
            pyautogui.keyDown('shift')
            self.shift_held = True
            self._log_important("⇧ Shift зажат")
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 4. Наводим мышь на предмет
            self._move_to_position_silent(item_pos)
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

            # 5. ЦИКЛ применения валюты
            for attempt in range(1, max_attempts + 1):
                if not self._check_safety_continuous():
                    self._log_important("🚨 Прервано по F12")
                    self._release_shift()
                    return False

                # ЛЕВАЯ кнопка мыши по предмету
                pyautogui.mouseDown(button='left')
                time.sleep(random.uniform(min_delay, max_delay))
                pyautogui.mouseUp(button='left')

                # Обновляем время последнего действия
                if self.safety:
                    self.safety.last_action_time = time.time()

                # Пауза для обновления игры
                time.sleep(0.1)

                # Проверяем моды
                if attempt % 5 == 0 or attempt == max_attempts:
                    self._log_important(f"🔍 Проверка модов (попытка {attempt})")

                if self._check_for_desired_mod(target_mods, mods_region):
                    self._log_important(f"🎉 Нужный мод найден! Попытка: {attempt}")
                    self._release_shift()
                    return True

                # Пауза между применениями
                if attempt < max_attempts:
                    time.sleep(random.uniform(min_delay, max_delay))

            self._log_important(f"❌ Целевой мод не найден за {max_attempts} попыток")
            self._release_shift()
            return False

        except Exception as e:
            self._release_shift()
            self._log_important(f"❌ Ошибка в цикле крафта: {e}")
            return False

    @classmethod
    def _move_to_position_silent(cls, position):
        """Наводим мышь без сообщений"""
        x, y = position
        variance = random.randint(3, 8)
        offset_x = random.randint(-variance, variance)
        offset_y = random.randint(-variance, variance)

        move_duration = random.uniform(0.2, 0.4)
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

    @classmethod
    def _log_important(cls, message):
        """Логирует только важные сообщения"""
        print(f"[Craft] {message}")

    def _check_for_desired_mod(self, target_mods, scan_region=None):
        """Проверяет наличие нужных модов через сканер"""
        if not target_mods or not self.scanner:
            return False

        try:
            # Используем переданную область или дефолтную
            if scan_region:
                mods = self.scanner.scan_item(scan_region)
            else:
                mods = self.scanner.scan_item_mods(self.scan_region)

            if mods:
                found = self.scanner.has_desired_mod(mods, target_mods)
                return found
            return False

        except Exception as e:
            self._log_important(f"⚠️ Ошибка проверки модов: {e}")
            return False

    def _check_safety_continuous(self):
        """Проверка безопасности включая F12"""
        if not self.safety:
            return True

        # Проверяем F12
        if hasattr(self.safety, 'check_emergency_stop_requested') and self.safety.check_emergency_stop_requested():
            return False

        # Проверяем другие условия безопасности
        if hasattr(self.safety, 'check_all_safety_conditions'):
            return self.safety.check_all_safety_conditions()

        return True

    def _release_shift(self):
        """Отпускает Shift если зажат"""
        if self.shift_held:
            pyautogui.keyUp('shift')
            self.shift_held = False
            self._log_important("⇧ Shift отпущен")

    @classmethod
    def _move_to_position(cls, position, target_name):
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
        self.is_mass_crafting = False
        show_message("🛑 Крафт принудительно остановлен")

    def stop_mass_craft(self):
        """Остановка массового крафта"""
        self.is_mass_crafting = False
        show_message("⏹️ Остановка массового крафта...")

    def get_mass_craft_progress(self):
        """Возвращает прогресс массового крафта"""
        if not self.item_slots:
            return 0

        total = len(self.item_slots)
        if total == 0:
            return 0

        return (self.current_item_index / total) * 100

    def get_stats(self):
        """Возвращает статистику контроллера"""
        return {
            'total_actions': self.action_count,
            'shift_held': self.shift_held,
            'mass_crafting': self.is_mass_crafting,
            'current_item': self.current_item_index,
            'total_items': len(self.item_slots),
            'successful_crafts': len(self.successful_crafts),
            'status': 'active'
        }
