import mss
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

        # УЛУЧШЕННЫЕ настройки OCR
        self.ocr_config = (r'--oem 3 --psm 8 -c '
                           r'tessedit_char_whitelist='
                           r'abcdefghijklmnopqrstuvwxyz'
                           r'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+% '
                           r'-c preserve_interword_spaces=1')

        # Целевые моды для поиска
        self.common_prefixes = ["increased", "added", "additional", "enhanced", "supported", "faster", "to"]
        self.common_suffixes = ["damage", "speed", "critical", "resistance", "life", "mana", "armour", "evasion",
                                "accuracy", "rating"]

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
        # УВЕЛИЧИВАЕМ смещения и размеры
        mods_offset_x = -50  # больше отступ
        mods_offset_y = -50  # больше отступ
        mods_width = 800  # шире область
        mods_height = 150  # выше область

        mods_x = item_x + mods_offset_x
        mods_y = item_y + mods_offset_y

        return {
            'left': mods_x,
            'top': mods_y,
            'width': mods_width,
            'height': mods_height
        }

    def scan_item(self, scan_region):
        """Сканирует моды предмета"""
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

            # УЛУЧШЕННАЯ обработка изображения
            processed_image = self._preprocess_image(screenshot)

            # УЛУЧШЕННОЕ распознавание текста
            text = self._extract_text(processed_image)

            # УЛУЧШЕННЫЙ парсинг модов
            mods = self._parse_mods(text)

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

            # УВЕЛИЧИВАЕМ область захвата для надежности
            expanded_region = {
                'left': max(0, int(x - 5)),  # расширяем слева
                'top': max(0, int(y - 5)),  # расширяем сверху
                'width': int(w + 10),  # расширяем ширину
                'height': int(h + 10)  # расширяем высоту
            }

            try:
                with mss.mss() as sct:
                    screenshot = sct.grab(expanded_region)
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

            # УВЕЛИЧИВАЕМ область для fallback
            x = max(0, x - 5)
            y = max(0, y - 5)
            w = w + 10
            h = h + 10

            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            screenshot.save('scanner_capture_fallback.png')
            print("✅ Скриншот сохранен (fallback): scanner_capture_fallback.png")
            return screenshot
        except Exception as e:
            print(f"❌ Ошибка fallback захвата: {e}")
            return None

    @classmethod
    def _preprocess_image(cls, image):
        """УЛУЧШЕННАЯ подготовка изображения для OCR"""
        try:
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # УЛУЧШЕННОЕ увеличение контраста
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # УЛУЧШЕННАЯ бинаризация
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # УЛУЧШЕННОЕ удаление шума
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            # ДОБАВЛЯЕМ резкость
            kernel_sharp = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(cleaned, -1, kernel_sharp)

            return sharpened
        except Exception as e:
            print(f"❌ Ошибка обработки изображения: {e}")
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    def _extract_text(self, image):
        """УЛУЧШЕННОЕ извлечение текста"""
        try:
            # Пробуем разные PSM режимы
            text1 = pytesseract.image_to_string(image, config=self.ocr_config, lang='eng')

            # Пробуем другой PSM режим
            alt_config = r'--oem 3 --psm 6'
            text2 = pytesseract.image_to_string(image, config=alt_config, lang='eng')

            # Выбираем лучший результат
            if len(text1.strip()) > len(text2.strip()):
                return text1.strip()
            else:
                return text2.strip()

        except Exception as e:
            show_message(f"❌ Ошибка OCR: {e}")
            return ""

    @classmethod
    def _parse_mods(cls, text):
        """УЛУЧШЕННЫЙ парсинг модов"""
        mods = []

        if not text:
            print("❌ Текст для парсинга пустой")
            return mods

        print(f"📝 Исходный текст для парсинга: '{text}'")

        lines = text.split('\n')

        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 2:  # УМЕНЬШАЕМ минимальную длину
                # УЛУЧШЕННАЯ проверка: больше ключевых слов
                has_numbers = any(char.isdigit() for char in line_clean)
                has_letters = any(char.isalpha() for char in line_clean)

                # РАСШИРЕННЫЙ список ключевых слов
                mod_keywords = [
                    'bow', 'arrow', 'accuracy', 'critical', 'damage', 'speed',
                    'resistance', 'life', 'mana', 'armour', 'evasion', 'gem',
                    'additional', 'increased', 'reduced', 'faster', 'to',
                    'physical', 'fire', 'cold', 'lightning', 'chaos', 'elemental',
                    'melee', 'attack', 'cast', 'spell', 'projectile', 'minion',
                    'quality', 'duration', 'radius', 'area', 'strength', 'dexterity',
                    'intelligence', 'attribute', 'chance', 'leech', 'regen'
                ]

                has_keyword = any(keyword in line_clean.lower() for keyword in mod_keywords)

                # УПРОЩАЕМ логику: добавляем если есть буквы и что-то осмысленное
                if has_letters and (has_numbers or has_keyword or len(line_clean) > 10):
                    clean_mod = ' '.join(line_clean.split())
                    # ФИЛЬТРУЕМ очевидный мусор
                    if not any(bad in clean_mod.lower() for bad in ['zzz', 'aaa', 'xxx', '...']):
                        mods.append(clean_mod)
                        print(f"✅ Добавлен мод: '{clean_mod}'")

        print(f"📄 Всего распознано модов: {len(mods)}")
        return mods

    @classmethod
    def has_desired_mod(cls, mods, target_mods):
        """УЛУЧШЕННАЯ проверка целевых модов"""
        if not mods or not target_mods:
            return False

        for mod in mods:
            mod_lower = mod.lower()
            print(f"🔍 DEBUG: Проверяем мод: '{mod_lower}'")

            for target in target_mods:
                target_lower = target.lower()
                print(f"🔍 DEBUG: Ищем '{target_lower}' в '{mod_lower}'")

                # УЛУЧШАЕМ поиск: частичное совпадение
                if (target_lower in mod_lower or
                        any(word in mod_lower for word in target_lower.split()) or
                        cls._fuzzy_match(mod_lower, target_lower)):
                    show_message(f"🎯 Найден целевой мод: {mod}")
                    return True

        print("❌ Совпадений не найдено")
        return False

    @classmethod
    def _fuzzy_match(cls, text, pattern):
        """Нечеткое совпадение для OCR ошибок"""
        # Простые замены частых ошибок OCR
        corrections = {
            '0': 'o', '1': 'i', '5': 's', '8': 'b',
            'tt': 't', 'ii': 'i', 'oo': 'o', 'vv': 'w'
        }

        corrected_text = text
        for wrong, right in corrections.items():
            corrected_text = corrected_text.replace(wrong, right)

        return pattern in corrected_text

    # Остальные методы без изменений
    def check_target_mods(self, current_mods, target_mods):
        return self.has_desired_mod(current_mods, target_mods)

    @classmethod
    def _image_hash(cls, image):
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
        return {
            'total_scans': self.scan_count,
            'status': 'active'
        }

    def update_config(self, new_config):
        self.config = new_config
        print("✅ Конфигурация сканера обновлена")
