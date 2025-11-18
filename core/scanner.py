import mss
import re
from PIL import Image
import cv2
import numpy as np
import pytesseract
from utils.helpers import show_message


class ItemScanner:
    def __init__(self, safety_manager=None):
        self.safety = safety_manager
        self.scan_count = 0
        self.sct = mss.mss()
        self.right_monitor = self._find_right_monitor()

        # Настройки OCR
        self.ocr_config = (r'--oem 3 --psm 6 -c '
                           r'tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+%')

        # Целевые моды для поиска
        self.common_prefixes = ["increased", "added", "additional", "enhanced", "supported", "faster", "to"]
        self.common_suffixes = ["damage", "speed", "critical", "resistance", "life", "mana", "armour", "evasion",
                                "accuracy", "rating"]

        # Кэш
        self.last_scan_hash = None
        self.last_scan_result = None

    def _find_right_monitor(self):
        """Находит самый правый монитор"""
        monitors = self.sct.monitors
        if len(monitors) <= 1:
            return monitors[0]

        # Находим монитор с наибольшим значением left (самый правый)
        rightmost = max(monitors[1:], key=lambda m: m['left'])
        print(f"🎯 Выбран правый монитор: left={rightmost['left']}, size={rightmost['width']}x{rightmost['height']}")
        return rightmost

    def scan_item(self, scan_region):
        """Сканирует моды предмета на правом мониторе"""
        try:
            # Проверяем безопасность
            if self.safety and not self.safety.check_all_safety_conditions():
                return []

            show_message("📷 Сканирование предмета...")

            # Захватываем screenshot на правом мониторе
            screenshot = self._capture_region_mss(scan_region)
            if screenshot is None:
                return []

            # Проверяем, не сканировали ли мы уже это состояние
            current_hash = self._image_hash(screenshot)
            if current_hash == self.last_scan_hash:
                show_message("⚡ Используем кэшированный результат")
                return self.last_scan_result

            # Обрабатываем изображение
            processed_image = self._preprocess_image(screenshot)

            # Распознаем текст
            text = self._extract_text(processed_image)

            # Парсим моды
            mods = self._parse_mods(text)

            # Сохраняем в кэш
            self.last_scan_hash = current_hash
            self.last_scan_result = mods

            self.scan_count += 1

            # Записываем действие в систему безопасности
            if self.safety:
                self.safety.record_action(success=True, action_type="item_scan")

            show_message(f"📄 Найдено модов: {len(mods)}")
            return mods

        except Exception as e:
            show_message(f"❌ Ошибка сканирования: {e}")
            if self.safety:
                self.safety.record_action(success=False, action_type="scan_error")
            return []

    def _capture_region_mss(self, region):
        """Захватывает область используя mss"""
        try:
            x, y, w, h = region

            print(f"📷 Захват региона: x={x}, y={y}, w={w}, h={h}")
            print(f"📺 Правый монитор: {self.right_monitor}")

            # 🔧 ПРОСТОЙ ПОДХОД: используем координаты как есть
            # MSS сам разберется с мультимониторной конфигурацией
            monitor_region = {
                'left': x,
                'top': y,
                'width': w,
                'height': h
            }

            screenshot = self.sct.grab(monitor_region)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Сохраняем оригинальный скриншот для отладки
            img.save('scanner_original.png')
            print("✅ Оригинальный скриншот сохранен: scanner_original.png")

            return img

        except Exception as e:
            print(f"❌ Ошибка захвата mss: {e}")
            return None

    def _preprocess_image(self, image):
        """Подготавливает изображение для OCR - УПРОЩЕННАЯ ВЕРСИЯ"""
        try:
            # Конвертируем в numpy array для OpenCV
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # 🔧 ПРОСТОЙ ПОДХОД: конвертируем в grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 🔧 ДОБАВЛЯЕМ ПРОВЕРКУ: если изображение слишком темное/светлое
            avg_brightness = np.mean(gray)
            print(f"📊 Средняя яркость: {avg_brightness}")

            if avg_brightness > 200:  # Слишком белое
                # 🔧 УМЕНЬШАЕМ ЯРКОСТЬ
                gray = cv2.convertScaleAbs(gray, alpha=0.7, beta=0)
            elif avg_brightness < 50:  # Слишком темное
                # 🔧 УВЕЛИЧИВАЕМ ЯРКОСТЬ
                gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=20)

            # 🔧 ПРОСТАЯ бинаризация вместо адаптивной
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Сохраняем для отладки
            cv2.imwrite('scanner_processed.png', binary)
            print("✅ Обработанное изображение сохранено")

            return binary

        except Exception as e:
            print(f"❌ Ошибка обработки изображения: {e}")
            # Fallback: возвращаем оригинал в grayscale
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    def _extract_text(self, image):
        """Извлекает текст из изображения"""
        try:
            text = pytesseract.image_to_string(image, config=self.ocr_config, lang='eng')
            return text
        except Exception as e:
            show_message(f"❌ Ошибка OCR: {e}")
            return ""

    def _parse_mods(self, text):
        """Парсит текст и извлекает моды - УЛУЧШЕННАЯ ВЕРСИЯ"""
        mods = []

        if not text:
            print("❌ Текст для парсинга пустой")
            return mods

        print(f"📝 Исходный текст: '{text}'")

        lines = text.split('\n')

        for line in lines:
            line_clean = line.strip()

            # 🔧 УЛУЧШЕНИЕ: более гибкие критерии для модов
            if len(line_clean) > 3:  # Увеличиваем минимальную длину
                # Ищем комбинации букв и цифр (типично для модов PoE)
                has_letters = any(c.isalpha() for c in line_clean)
                has_digits = any(c.isdigit() for c in line_clean)
                has_special = any(c in '+%' for c in line_clean)  # Проценты и плюсы

                # Считаем модом если есть буквы + (цифры или специальные символы)
                if has_letters and (has_digits or has_special):
                    clean_mod = ' '.join(line_clean.split())
                    mods.append(clean_mod)
                    print(f"✅ Добавлен мод: '{clean_mod}'")

        print(f"📄 Всего распознано модов: {len(mods)}")
        return mods

    def _is_likely_mod(self, text):
        """Проверяет, похож ли текст на мод из PoE"""
        text_lower = text.lower()

        # Проверяем наличие ключевых слов
        has_prefix = any(prefix in text_lower for prefix in self.common_prefixes)
        has_suffix = any(suffix in text_lower for suffix in self.common_suffixes)
        has_numbers = bool(re.search(r'\d+', text))  # Есть числа (проценты, значения)

        # Считаем похожим на мод если есть либо префикс+числа, либо суффикс+числа
        return (has_prefix or has_suffix) and has_numbers

    def has_desired_mod(self, mods, target_mods):
        """Проверяет, есть ли среди модов целевые"""
        if not mods or not target_mods:
            return False

        for mod in mods:
            mod_lower = mod.lower()
            for target in target_mods:
                if target.lower() in mod_lower:
                    show_message(f"🎯 Найден целевой мод: {mod}")
                    return True

        return False

    def _image_hash(self, image):
        """Создает простой хэш изображения для кэширования"""
        try:
            # Конвертируем в grayscale и ресайзим для быстрого хэширования
            small = image.resize((8, 8), Image.Resampling.LANCZOS)
            grayscale = small.convert('L')

            # Вычисляем среднюю яркость
            pixels = list(grayscale.getdata())
            avg = sum(pixels) / len(pixels)

            # Создаем битовый хэш
            bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            return int(bits, 2)
        except:
            return 0

    def get_stats(self):
        """Возвращает статистику сканера"""
        return {
            'total_scans': self.scan_count,
            'status': 'active'
        }
