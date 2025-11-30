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
        self.currency_position = None
        self.target_mods = None

    def set_scanner(self, scanner):
        """Устанавливает сканер для проверки модов"""
        self.scanner = scanner

    def set_scan_region(self, scan_region):
        """Устанавливает регион сканирования"""
        self.scan_region = scan_region

    def set_item_slots(self, item_slots, grid_corners=None):
        """Устанавливает слоты предметов для массового крафта"""
        if grid_corners:
            # Если переданы углы сетки, вычисляем координаты
            top_left, bottom_right = grid_corners
            self.item_slots = self.calculate_grid_positions(top_left, bottom_right)
            show_message(f"📦 Вычислено {len(self.item_slots)} слотов по сетке")
        else:
            # Иначе используем переданные слоты
            self.item_slots = item_slots
            show_message(f"📦 Загружено {len(item_slots)} слотов предметов")

        # Отладочная информация
        print("🎯 ФИНАЛЬНЫЕ КООРДИНАТЫ ПРЕДМЕТОВ:")
        for i, pos in enumerate(self.item_slots):
            print(f"  {i + 1:2d}. ({pos[0]:4d}, {pos[1]:4d})")

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
        self.currency_position = currency_pos
        self.target_mods = target_mods

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

            # ✅ ЗАЖИМАЕМ SHIFT ОДИН РАЗ В НАЧАЛЕ ЦИКЛА
            self._log_important("⇧ ЗАЖИМАЕМ SHIFT ДЛЯ ВСЕГО ЦИКЛА КРАФТА")
            pyautogui.keyDown('shift')
            self.shift_held = True
            time.sleep(0.3)

            # ✅ ПЕРВЫЙ ПРЕДМЕТ: БЕРЕМ ВАЛЮТУ И ПЕРЕХОДИМ НА ВКЛАДКУ
            first_item_success = self._craft_first_item(currency_pos, self.item_slots[0], target_mods,
                                                        max_attempts_per_item)

            if first_item_success:
                self.successful_crafts.append({
                    'item_index': 0,
                    'position': self.item_slots[0],
                    'timestamp': time.time()
                })
                show_message(f"✅ Предмет 1 успешно прокрафтен!")
            else:
                show_message(f"❌ Предмет 1 не удалось прокрафтить")

            # ✅ ОСТАЛЬНЫЕ ПРЕДМЕТЫ: ПРОСТО ПЕРЕХОДИМ И КРАФТИМ (SHIFT УЖЕ ЗАЖАТ)
            for item_index in range(1, total_items):
                if not self.is_mass_crafting or (self.safety and self.safety.check_emergency_stop_requested()):
                    show_message("🚨 Прервано по F12")
                    break

                self.current_item_index = item_index
                item_pos = self.item_slots[item_index]
                show_message(f"🔧 Обработка предмета {item_index + 1}/{total_items}")

                # ✅ ПРОСТО ПЕРЕХОДИМ К СЛЕДУЮЩЕМУ ПРЕДМЕТУ (ВАЛЮТА УЖЕ В КУРСОРЕ, SHIFT ЗАЖАТ)
                success = self._craft_next_item_only(item_pos, target_mods, max_attempts_per_item)

                if success:
                    self.successful_crafts.append({
                        'item_index': item_index,
                        'position': item_pos,
                        'timestamp': time.time()
                    })
                    show_message(f"✅ Предмет {item_index + 1} успешно прокрафтен!")
                else:
                    if self.safety and self.safety.check_emergency_stop_requested():
                        show_message("🚨 Прервано по F12")
                        break
                    show_message(f"❌ Предмет {item_index + 1} не удалось прокрафтить")

            # ✅ ОТПУСКАЕМ SHIFT ТОЛЬКО ПОСЛЕ ВСЕХ ПРЕДМЕТОВ
            self._release_shift()

            # Завершение массового крафта
            self.is_mass_crafting = False
            success_count = len(self.successful_crafts)
            show_message(f"🎉 Массовый крафт завершен! Успешно: {success_count}/{total_items}")

        except Exception as e:
            self._release_shift()
            self.is_mass_crafting = False
            show_message(f"❌ Ошибка в массовом крафте: {e}")

    @classmethod
    def calculate_grid_positions(cls, top_left_pos, bottom_right_pos):
        """
        Вычисляет координаты всех предметов в сетке 6x3
        на основе РЕАЛЬНЫХ данных калибровки
        """
        try:
            top_left_x, top_left_y = top_left_pos
            bottom_right_x, bottom_right_y = bottom_right_pos

            # Вычисляем РЕАЛЬНЫЕ размеры сетки
            grid_width = bottom_right_x - top_left_x
            grid_height = bottom_right_y - top_left_y

            # 🔧 РЕАЛЬНЫЕ размеры предмета (из ваших координат)
            item_width = 100  # 2084 - 1984 = 100px
            item_height = 198  # 445 - 247 = 198px

            print(f"🔧 Размер сетки: {grid_width}x{grid_height}")
            print(f"🔧 Реальный размер предмета: {item_width}x{item_height}")

            item_positions = []

            # Генерируем координаты для сетки 6x3
            for row in range(3):  # 3 ряда
                for col in range(6):  # 6 столбцов
                    # 🔧 ВЫЧИСЛЯЕМ РЕАЛЬНЫЕ КООРДИНАТЫ
                    center_x = top_left_x + (col * item_width) + (item_width // 2)
                    center_y = top_left_y + (row * item_height) + (item_height // 2)

                    item_positions.append((center_x, center_y))
                    print(
                        f"🔧 Предмет {len(item_positions)}: ({center_x}, {center_y}) - ряд {row + 1}, колонка {col + 1}")

            return item_positions

        except Exception as e:
            show_message(f"❌ Ошибка вычисления сетки: {e}")
            return []

    def _craft_first_item(self, currency_pos, item_pos, target_mods, max_attempts):
        """Крафт ПЕРВОГО предмета с взятием валюты и переходом на вкладку"""
        try:
            # 1. Правый клик по валюте (ТОЛЬКО ДЛЯ ПЕРВОГО ПРЕДМЕТА)
            self._log_important("💰 Правый клик по валюте (первый предмет)")
            self._move_to_position_silent(currency_pos)
            if not self._check_safety_continuous():
                return False

            pyautogui.mouseDown(button='right')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='right')
            time.sleep(0.3)

            # 2. Перемещаемся на вкладку stash
            self._log_important("📁 Переходим на вкладку stash")
            self._move_to_position_silent(self.stash_tab_position)
            if not self._check_safety_continuous():
                return False
            time.sleep(0.3)

            # 3. Левый клик по вкладке
            self._log_important("👆 Левый клик по вкладке")
            pyautogui.mouseDown(button='left')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='left')
            time.sleep(0.3)

            # 4. Наводимся на первый предмет
            self._log_important("🎯 Наводимся на первый предмет")
            self._move_to_position_silent(item_pos)
            if not self._check_safety_continuous():
                return False
            time.sleep(0.3)

            # 5. Цикл крафта для первого предмета
            success = self._craft_item_cycle(target_mods, max_attempts, item_pos)

            return success

        except Exception as e:
            show_message(f"❌ Ошибка крафта первого предмета: {e}")
            return False

    def _craft_next_item_only(self, item_pos, target_mods, max_attempts):
        try:
            self._log_important(f"🎯 Переходим к предмету {self.current_item_index + 1}")

            current_x, current_y = pyautogui.position()
            target_x, target_y = item_pos

            print(f"🔧 Текущая позиция: ({current_x}, {current_y})")
            print(f"🔧 Целевая позиция: ({target_x}, {target_y})")
            print(f"🔧 Разница по X: {target_x - current_x} пикселей")

            # 🔧 УВЕЛИЧИВАЕМ СМЕЩЕНИЕ МЕЖДУ ПРЕДМЕТАМИ
            # Для гарантированного перехода к следующему предмету
            new_x = target_x
            new_y = target_y

            move_duration = random.uniform(0.3, 0.5)
            pyautogui.moveTo(new_x, new_y, duration=move_duration)

            if not self._check_safety_continuous():
                return False

            time.sleep(0.8)

            success = self._craft_item_cycle(target_mods, max_attempts, item_pos)
            return success

        except Exception as e:
            show_message(f"❌ Ошибка крафта предмета {self.current_item_index + 1}: {e}")
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

            # Левый клик по предмету (применяем валюту) - Shift УЖЕ ЗАЖАТ
            pyautogui.mouseDown(button='left')
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.mouseUp(button='left')

            # Обновляем время последнего действия
            if self.safety:
                self.safety.last_action_time = time.time()

            # Пауза для обновления игры
            time.sleep(0.2)

            # Проверяем моды
            if attempt or attempt == max_attempts:
                self._log_important(f"🔍 Проверка модов (попытка {attempt})")

            if self._check_for_desired_mod(target_mods, mods_region):
                self._log_important(f"🎉 Нужный мод найден! Попытка: {attempt}")
                return True

            # Пауза между применениями
            if attempt < max_attempts:
                time.sleep(random.uniform(0.1, 0.2))

        self._log_important(f"❌ Целевой мод не найден за {max_attempts} попыток")
        return False

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
                # ✅ ДЕТАЛЬНАЯ ОТЛАДКА: что распозналось
                self._log_important(f"🔍 Распознанные моды ({len(mods)}):")
                for i, mod in enumerate(mods):
                    self._log_important(f"   {i + 1}. '{mod}'")

                # Используем стандартный метод сканера
                found = self.scanner.has_desired_mod(mods, target_mods)
                return found

            self._log_important("❌ Моды не найдены")
            return False

        except Exception as e:
            self._log_important(f"⚠️ Ошибка проверки модов: {e}")
            return False

    @classmethod
    def _move_to_position_silent(cls, position):
        """Перемещение с маленьким рандомом"""
        x, y = position

        # Текущая позиция мыши
        current_x, current_y = pyautogui.position()

        # Если мышь уже близко к цели - не двигаем
        distance = ((current_x - x) ** 2 + (current_y - y) ** 2) ** 0.5
        if distance < 10:
            print(f"🔧 Мышь уже близко к цели ({distance:.1f} px), пропускаем перемещение")
            return

        # 🔧 МАЛЕНЬКИЙ РАНДОМ: 2-6 пикселей
        variance_x = random.randint(2, 6)
        variance_y = random.randint(2, 4)

        offset_x = random.randint(-variance_x, variance_x)
        offset_y = random.randint(-variance_y, variance_y)

        # Короткое перемещение
        move_duration = random.uniform(0.2, 0.4)

        # Прямое перемещение
        pyautogui.moveTo(x + offset_x, y + offset_y, duration=move_duration)

        print(f"🔧 Перемещение: ({current_x}, {current_y}) -> ({x + offset_x}, {y + offset_y})")
        print(f"🔧 Маленький разброс: X={variance_x}, Y={variance_y}")

    @classmethod
    def _log_important(cls, message):
        """Логирует только важные сообщения"""
        print(f"[Craft] {message}")

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

    # Остальные методы для совместимости
    def use_currency(self, currency_pos, item_pos, max_attempts=50, target_mods=None, min_delay=0.1, max_delay=0.2):
        """Использует валюту на предмете - ОСНОВНОЙ МЕТОД (совместимость)"""
        try:
            if self.safety and self.safety.check_emergency_stop_requested():
                show_message("🚨 ОСТАНОВКА ПО F12")
                return False

            show_message(f"🔄 Запуск цикла крафта (макс. {max_attempts} попыток)")

            success = self._use_currency_cycle(currency_pos, item_pos, max_attempts, target_mods, min_delay, max_delay,
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
        """Цикл крафта для обычного режима"""
        self._log_important("⚡ Начинаем цикл крафта...")

        try:
            # 1. Наводим мышь на валюту
            self._move_to_position_silent(currency_pos)
            if not self._check_safety_continuous():
                self._release_shift()
                return False
            time.sleep(0.3)

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
                time.sleep(0.5)

                # Проверяем моды
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
