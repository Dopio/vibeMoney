import mss
import re
from PIL import Image
import cv2
import numpy as np
import easyocr
from utils.helpers import show_message
import pyautogui


class ItemScanner:
    def __init__(self, safety_manager=None, config=None):
        self.safety = safety_manager
        self.config = config or {}
        self.scan_count = 0
        self.right_monitor = self._find_right_monitor()

        # Инициализация EasyOCR
        try:
            self.reader = easyocr.Reader(['en'])
            print("✅ EasyOCR успешно инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации EasyOCR: {e}")
            self.reader = None

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

    @classmethod
    def _find_right_monitor(cls):
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
        mods_offset_x = -700  # широта
        mods_offset_y = -170  # высота
        mods_width = 1200  # Шире для захвата полных модов
        mods_height = 200  # Выше для захвата нескольких строк

        mods_x = item_x + item_width + mods_offset_x
        mods_y = item_y + item_height + mods_offset_y

        return {
            'left': mods_x,
            'top': mods_y,
            'width': mods_width,
            'height': mods_height
        }

    def scan_item(self, scan_region):
        """Сканирует моды предмета с использованием EasyOCR"""
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
            processed_image = self._preprocess_image_easyocr(screenshot)

            # Распознавание текста с EasyOCR
            mods = self._extract_text_easyocr(processed_image)

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

    @classmethod
    def _preprocess_image_easyocr(cls, image):
        """Подготовка изображения для EasyOCR"""
        try:
            # Конвертируем PIL Image в numpy array
            img_array = np.array(image)

            # Конвертируем RGB to BGR для OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            # Увеличиваем контраст
            lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l_contrast = clahe.apply(l)
            lab_contrast = cv2.merge([l_contrast, a, b])
            enhanced = cv2.cvtColor(lab_contrast, cv2.COLOR_LAB2BGR)

            # Увеличиваем резкость
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)

            # Увеличиваем размер для лучшего распознавания
            scale_percent = 150
            width = int(sharpened.shape[1] * scale_percent / 100)
            height = int(sharpened.shape[0] * scale_percent / 100)
            resized = cv2.resize(sharpened, (width, height), interpolation=cv2.INTER_CUBIC)

            return resized

        except Exception as e:
            print(f"❌ Ошибка обработки изображения: {e}")
            return np.array(image)

    def _extract_text_easyocr(self, image):
        """Извлечение текста с помощью EasyOCR"""
        if self.reader is None:
            print("❌ EasyOCR не инициализирован")
            return []

        try:
            # Распознаем текст с оптимизированными настройками для PoE
            results = self.reader.readtext(
                image,
                detail=1,
                paragraph=False,
                min_size=20,  # Минимальный размер текста
                text_threshold=0.6,  # Порог уверенности для текста
                low_text=0.4,  # Порог для слабого текста
                link_threshold=0.4,  # Порог для связывания символов
                canvas_size=1600  # Размер канауса для обработки
            )

            # Собираем все распознанные тексты
            all_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Низкий порог для PoE текста
                    clean_text = self._clean_poe_text(text)
                    if clean_text and len(clean_text) >= 3:
                        all_texts.append({
                            'text': clean_text,
                            'confidence': confidence,
                            'bbox': bbox
                        })
                        print(f"📖 EasyOCR: '{clean_text}' (уверенность: {confidence:.2f})")

            # Парсим моды из распознанного текста
            mods = self._parse_mods_easyocr(all_texts)
            return mods

        except Exception as e:
            print(f"❌ Ошибка EasyOCR: {e}")
            return []

    def _parse_mods_easyocr(self, text_results):
        """Парсит моды из результатов EasyOCR"""
        mods = []

        if not text_results:
            return mods

        # Сортируем по Y координате (сверху вниз)
        sorted_texts = sorted(text_results, key=lambda x: x['bbox'][0][1])

        found_requires = False

        for item in sorted_texts:
            text = item['text']
            confidence = item['confidence']

            # Ищем строку "REQUIRES LEVEL"
            if 'requires level' in text.lower():
                found_requires = True
                print("✅ Найдена строка REQUIRES LEVEL - начинаем сбор модов")
                continue

            # Если нашли REQUIRES LEVEL, собираем последующие строки как моды
            if found_requires:
                # Проверяем что это похоже на мод
                if self._is_valid_poe_mod(text):
                    mods.append(text)
                    print(f"✅ Добавлен мод: '{text}' (уверенность: {confidence:.2f})")

        # Если не нашли REQUIRES LEVEL, используем fallback
        if not mods:
            print("⚠️ REQUIRES LEVEL не найден, используем fallback парсинг")
            mods = self._parse_mods_fallback_easyocr(text_results)

        return mods

    def _parse_mods_fallback_easyocr(self, text_results):
        """Fallback парсинг для EasyOCR"""
        mods = []

        for item in text_results:
            text = item['text']
            confidence = item['confidence']

            if self._is_valid_poe_mod(text) and confidence > 0.4:
                mods.append(text)
                print(f"✅ Fallback мод: '{text}' (уверенность: {confidence:.2f})")

        return mods

    def _is_valid_poe_mod(self, text):
        """Проверяет, что текст похож на PoE мод"""
        if len(text) < 4:
            return False

        # Должен содержать буквы
        has_letters = any(c.isalpha() for c in text)
        # Должен содержать цифры или %
        has_numbers_or_percent = any(c.isdigit() or c == '%' for c in text)

        if not (has_letters and has_numbers_or_percent):
            return False

        # Проверяем наличие ключевых слов PoE
        text_lower = text.lower()
        has_poe_keyword = any(keyword in text_lower for keyword in self.poe_mods_keywords)

        return has_poe_keyword

    @classmethod
    def _clean_poe_text(cls, text):
        """Очищает текст PoE"""
        # Убираем лишние символы, но сохраняем % и цифры
        cleaned = re.sub(r'[^\w\s%+\-]', '', text)
        # Заменяем множественные пробелы на один
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

    def has_desired_mod(self, mods, target_mods):
        """Проверка целевых модов"""
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

    @classmethod
    def _fuzzy_ocr_match(cls, ocr_text, target_pattern):
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

    @classmethod
    def _capture_region_fallback(cls, region):
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
            'status': 'active',
            'easyocr_ready': self.reader is not None
        }

    def update_config(self, new_config):
        """Обновляет конфигурацию сканера"""
        self.config = new_config
        print("✅ Конфигурация сканера обновлена")
