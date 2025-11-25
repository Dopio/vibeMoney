import mss
import re
from PIL import Image
import cv2
import numpy as np
import pytesseract
from utils.helpers import show_message
import pyautogui


class ItemScanner:
    def __init__(self, safety_manager=None, config=None):
        self.safety = safety_manager
        self.config = config or {}
        self.scan_count = 0
        self.right_monitor = self._find_right_monitor()

        # УЛУЧШЕННЫЕ настройки OCR для PoE
        self.ocr_config = r'--oem 3 --psm 6'

        # Расширенный список ключевых слов PoE
        self.poe_mods_keywords = [
            # Damage types
            'physical', 'fire', 'cold', 'lightning', 'chaos', 'elemental',
            'damage', 'attack', 'spell', 'projectile', 'melee', 'bow',

            # Stats
            'increased', 'more', 'additional', 'added', 'reduced', 'less',
            'critical', 'speed', 'accuracy', 'life', 'mana', 'armour',
            'evasion', 'energy', 'shield', 'resistance', 'strength',
            'dexterity', 'intelligence', 'attribute',

            # Mechanics
            'chance', 'duration', 'radius', 'area', 'quality', 'level',
            'gem', 'support', 'faster', 'slower', 'regen', 'leech',

            # Common mod parts
            'to', 'of', 'and', 'with', 'per', 'global', 'local',
            'maximum', 'minimum', 'increased', 'reduced'
        ]

        # Кэш
        self.last_scan_hash = None
        self.last_scan_result = None

    def _find_right_monitor(self):
        """Находит самый правый монитор"""
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if len(monitors) <= 1:
                    return monitors[0]

                rightmost = max(monitors[1:], key=lambda m: m['left'])
                print(f"🎯 Выбран правый монитор: left={rightmost['left']},"
                      f"size={rightmost['width']}x{rightmost['height']}")
                return rightmost
        except Exception as e:
            print(f"❌ Ошибка поиска монитора: {e}")
            return {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}

    def get_mods_region_for_item(self, item_x, item_y):
        """
        Вычисляет область сканирования модов для конкретного предмета
        """
        item_width = self.config.get('stash_item_width', 70)
        item_height = self.config.get('stash_item_height', 70)

        # Увеличиваем область сканирования для лучшего захвата
        mods_offset_x = 0
        mods_offset_y = 0
        mods_width = 600  # Шире для захвата полных модов
        mods_height = 150  # Выше для захвата нескольких строк

        mods_x = item_x + item_width + mods_offset_x
        mods_y = item_y + mods_offset_y

        return {
            'left': mods_x,
            'top': mods_y,
            'width': mods_width,
            'height': mods_height
        }

    def scan_item(self, scan_region):
        """Сканирует моды предмета с улучшенным OCR"""
        try:
            if self.safety and not self.safety.check_all_safety_conditions():
                return []

            show_message("📷 Сканирование предмета...")

            screenshot = self._capture_region_mss(scan_region)
            if screenshot is None:
                return []

            # Проверяем кэш
            current_hash = self._image_hash(screenshot)
            if current_hash == self.last_scan_hash:
                show_message("⚡ Используем кэшированный результат")
                return self.last_scan_result

            # Улучшенная обработка изображения
            processed_image = self._preprocess_image_improved(screenshot)

            # Распознавание текста с разными настройками
            text = self._extract_text_improved(processed_image)

            # Улучшенный парсинг модов
            mods = self._parse_mods_improved(text)

            print(f"🔍 DEBUG: Распознанный текст: '{text}'")
            print(f"🔍 DEBUG: Извлеченные моды: {mods}")

            # Сохраняем в кэш
            self.last_scan_hash = current_hash
            self.last_scan_result = mods

            self.scan_count += 1

            if self.safety:
                self.safety.record_action(success=True, action_type="item_scan")

            show_message(f"📄 Найдено модов: {len(mods)}")
            return mods

        except Exception as e:
            show_message(f"❌ Ошибка сканирования: {e}")
            if self.safety:
                self.safety.record_action(success=False, action_type="scan_error")
            return []

    def _preprocess_image_improved(self, image):
        """Улучшенная подготовка изображения для PoE текста"""
        try:
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Конвертируем в grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Увеличиваем контраст
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            contrast = clahe.apply(gray)

            # Бинаризация
            _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Убираем шум
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

            # Увеличиваем изображение для лучшего распознавания
            scale_percent = 150  # 150% увеличение
            width = int(cleaned.shape[1] * scale_percent / 100)
            height = int(cleaned.shape[0] * scale_percent / 100)
            resized = cv2.resize(cleaned, (width, height), interpolation=cv2.INTER_CUBIC)

            return resized

        except Exception as e:
            print(f"❌ Ошибка обработки изображения: {e}")
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    def _extract_text_improved(self, image):
        """Улучшенное извлечение текста"""
        try:
            # Пробуем разные настройки OCR
            texts = []

            # Настройка 1: Стандартная для PoE
            text1 = pytesseract.image_to_string(image, config=self.ocr_config, lang='eng')
            texts.append(text1)

            # Настройка 2: Single column
            text2 = pytesseract.image_to_string(image, config='--oem 3 --psm 4', lang='eng')
            texts.append(text2)

            # Настройка 3: Single word
            text3 = pytesseract.image_to_string(image, config='--oem 3 --psm 8', lang='eng')
            texts.append(text3)

            # Выбираем самый длинный текст (обычно самый точный)
            best_text = max(texts, key=lambda x: len(x.strip()))

            return best_text.strip()

        except Exception as e:
            show_message(f"❌ Ошибка OCR: {e}")
            return ""

    def _parse_mods_improved(self, text):
        """Улучшенный парсинг модов для PoE"""
        mods = []

        if not text:
            print("❌ Текст для парсинга пустой")
            return mods

        print(f"📝 Исходный текст для парсинга: '{text}'")

        lines = text.split('\n')

        for line in lines:
            line_clean = line.strip()

            # Более либеральные условия для PoE модов
            if len(line_clean) >= 3:  # Уменьшаем минимальную длину

                # Проверяем наличие ключевых слов PoE
                has_poe_keyword = any(keyword in line_clean.lower() for keyword in self.poe_mods_keywords)

                # Проверяем наличие цифр (процентов, значений)
                has_numbers = any(char.isdigit() for char in line_clean)

                # Проверяем наличие букв
                has_letters = any(char.isalpha() for char in line_clean)

                # Условия для включения в моды:
                # 1. Есть ключевое слово PoE И (цифры ИЛИ длина > 6)
                # 2. Есть цифры И буквы И длина > 5
                condition1 = has_poe_keyword and (has_numbers or len(line_clean) > 6)
                condition2 = has_numbers and has_letters and len(line_clean) > 5

                if condition1 or condition2:
                    clean_mod = ' '.join(line_clean.split())

                    # Фильтруем очевидный мусор
                    if not self._is_garbage_text(clean_mod):
                        mods.append(clean_mod)
                        print(f"✅ Добавлен мод: '{clean_mod}'")

        print(f"📄 Всего распознано модов: {len(mods)}")
        return mods

    def _is_garbage_text(self, text):
        """Фильтрует мусорный текст"""
        if len(text) < 3:
            return True

        text_lower = text.lower()

        # Очевидный мусор
        garbage_patterns = [
            r'^[^a-zA-Z0-9]*$',  # Только спецсимволы
            r'^[a-zA-Z]{1,2}$',  # Одна-две буквы
            r'^\d+$',  # Только цифры
        ]

        for pattern in garbage_patterns:
            if re.match(pattern, text_lower):
                return True

        # Дополнительные фильтры для PoE
        garbage_words = ['zzz', 'aaa', 'xxx', '...', '---', '___', '///', '\\\\']
        if any(word in text_lower for word in garbage_words):
            return True

        return False

    def has_desired_mod(self, mods, target_mods):
        """Улучшенная проверка целевых модов"""
        if not mods or not target_mods:
            print("❌ Нет модов или целевых модов для проверки")
            return False

        print(f"🎯 Ищем целевые моды: {target_mods}")
        print(f"📄 Проверяем {len(mods)} модов:")

        for i, mod in enumerate(mods):
            mod_lower = mod.lower()
            print(f"  {i + 1}. '{mod}' -> '{mod_lower}'")

            for target in target_mods:
                target_lower = target.lower()

                # Разные стратегии поиска
                exact_match = target_lower in mod_lower
                word_match = any(word in mod_lower for word in target_lower.split())
                fuzzy_match = self._fuzzy_ocr_match(mod_lower, target_lower)

                if exact_match:
                    print(f"🎯 Точное совпадение: '{target}' в '{mod}'")
                    show_message(f"🎯 Найден целевой мод: {mod}")
                    return True

                elif word_match:
                    print(f"🎯 Совпадение по словам: '{target}' в '{mod}'")
                    show_message(f"🎯 Найден целевой мод: {mod}")
                    return True

                elif fuzzy_match:
                    print(f"🎯 Нечеткое совпадение: '{target}' в '{mod}'")
                    show_message(f"🎯 Найден целевой мод: {mod}")
                    return True

        print("❌ Совпадений не найдено")
        return False

    def _fuzzy_ocr_match(self, ocr_text, target_pattern):
        """Нечеткое совпадение для обработки ошибок OCR"""
        if not ocr_text or not target_pattern:
            return False

        # Частые ошибки OCR в PoE
        corrections = {
            '0': 'o', '1': 'i', '5': 's', '8': 'b',
            'tt': 't', 'ii': 'i', 'oo': 'o', 'vv': 'w',
            'rn': 'm', 'cl': 'd'
        }

        corrected_text = ocr_text
        for wrong, right in corrections.items():
            corrected_text = corrected_text.replace(wrong, right)

        # Ищем частичное совпадение
        if target_pattern in corrected_text:
            return True

        # Ищем по словам
        target_words = target_pattern.split()
        for word in target_words:
            if len(word) > 3 and word in corrected_text:
                return True

        return False

    def scan_item_mods(self, scan_region=None):
        """Адаптер для совместимости с craft_controller"""
        if scan_region is None:
            default_region = self.config.get('default_scan_region')
            if default_region:
                scan_region = (
                    default_region['left'],
                    default_region['top'],
                    default_region['width'],
                    default_region['height']
                )
            else:
                scan_region = (
                    self.right_monitor['left'],
                    self.right_monitor['top'],
                    self.right_monitor['width'],
                    self.right_monitor['height']
                )

        if isinstance(scan_region, dict):
            region_tuple = (
                scan_region['left'],
                scan_region['top'],
                scan_region['width'],
                scan_region['height']
            )
        else:
            region_tuple = scan_region

        return self.scan_item(region_tuple)

    def _capture_region_mss(self, region):
        """Захватывает область с улучшенными настройками"""
        try:
            if isinstance(region, (list, tuple)) and len(region) == 4:
                x, y, w, h = region
            elif isinstance(region, dict):
                x = region.get('left', region.get('x', 0))
                y = region.get('top', region.get('y', 0))
                w = region.get('width', region.get('w', 100))
                h = region.get('height', region.get('h', 100))
            else:
                print(f"❌ Неизвестный формат региона: {region}")
                return None

            try:
                with mss.mss() as sct:
                    monitor_region = {
                        'left': int(x),
                        'top': int(y),
                        'width': int(w),
                        'height': int(h)
                    }

                    screenshot = sct.grab(monitor_region)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                    # Сохраняем для отладки
                    img.save('scanner_capture.png')
                    print("✅ Скриншот сохранен: scanner_capture.png")

                    return img

            except Exception as e:
                print(f"❌ Ошибка захвата mss (внутренняя): {e}")
                return self._capture_region_fallback(region)

        except Exception as e:
            print(f"❌ Ошибка захвата mss: {e}")
            return None

    def _capture_region_fallback(self, region):
        """Альтернативный метод захвата"""
        try:
            if isinstance(region, (list, tuple)) and len(region) == 4:
                x, y, w, h = region
            elif isinstance(region, dict):
                x = region.get('left', region.get('x', 0))
                y = region.get('top', region.get('y', 0))
                w = region.get('width', region.get('w', 100))
                h = region.get('height', region.get('h', 100))
            else:
                return None

            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot.save('scanner_capture_fallback.png')
            print("✅ Скриншот сохранен (fallback): scanner_capture_fallback.png")
            return screenshot
        except Exception as e:
            print(f"❌ Ошибка fallback захвата: {e}")
            return None

    def check_target_mods(self, current_mods, target_mods):
        """Адаптер для craft_controller"""
        return self.has_desired_mod(current_mods, target_mods)

    @classmethod
    def _image_hash(cls, image):
        """Создает хэш изображения для кэширования"""
        try:
            small = image.resize((8, 8), Image.Resampling.LANCZOS)
            grayscale = small.convert('L')
            pixels = list(grayscale.getdata())
            avg = sum(pixels) / len(pixels)
            bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            return int(bits, 2)
        except Exception as e:
            print(f'❌ Ошибка в _image_hash: {e}')
            return hash(str(image))

    def get_stats(self):
        """Возвращает статистику сканера"""
        return {
            'total_scans': self.scan_count,
            'status': 'active'
        }

    def update_config(self, new_config):
        """Обновляет конфигурацию сканера"""
        self.config = new_config
        print("✅ Конфигурация сканера обновлена")
