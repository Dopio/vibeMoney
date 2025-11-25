from .controller import CraftController
from .scanner import ItemScanner
from .safety import SafetyManager
from .analyzer import CraftAnalyzer
from utils.helpers import show_message


class PoeCraftBot:
    def __init__(self):
        self.config = None
        self.controller = None
        self.scanner = None
        self.safety = None
        self.analyzer = None
        self.running = False

    def initialize(self, config):
        """Инициализация бота с конфигом"""
        try:
            self.config = config
            self.safety = SafetyManager()
            self.scanner = ItemScanner(self.safety)
            self.controller = CraftController(self.safety)
            self.analyzer = CraftAnalyzer()

            # Связываем компоненты
            self.controller.set_scanner(self.scanner)

            if self.config.get('scan_region'):
                self.controller.set_scan_region(self.config['scan_region'])

            show_message("✅ Бот инициализирован")
            return True

        except Exception as e:
            show_message(f"❌ Ошибка инициализации бота: {e}")
            return False

    def start_crafting(self, max_attempts=None, target_mods=None):
        """Запуск автоматического крафта"""
        if not self.initialize(self.config):
            return False

        self.running = True
        show_message(f"🎮 Запуск крафта... Макс. попыток: {max_attempts or self.config.get('max_attempts', 50)}")

        try:
            # Используем переданные параметры или из конфига
            currency_pos = self.config.get('currency_position')
            item_pos = self.config.get('item_position')
            final_target_mods = target_mods or self.config.get('target_mods', ['crit'])
            final_max_attempts = max_attempts or self.config.get('max_attempts', 50)
            final_min_delay = self.config.get('min_delay', 0.1)
            final_max_delay = self.config.get('max_delay', 0.2)
            scan_region = self.config.get('scan_region')

            if not all([currency_pos, item_pos, scan_region]):
                show_message("❌ Не все настройки configured")
                return False

            # Запускаем цикл крафта через контроллер
            success = self.controller.use_currency(
                currency_pos=currency_pos,
                item_pos=item_pos,
                max_attempts=final_max_attempts,
                target_mods=final_target_mods,
                min_delay=final_min_delay,
                max_delay=final_max_delay
            )

            # Записываем результат в анализатор
            self.analyzer.record_craft(
                attempt=final_max_attempts,
                mods_found=[],
                target_mod_found=success,
                currency_used="orb_of_alteration"
            )

            return success

        except Exception as e:
            show_message(f"❌ Ошибка в цикле крафта: {e}")
            return False
        finally:
            self.running = False

    def stop_crafting(self):
        """Остановка бота"""
        self.running = False
        if self.controller:
            self.controller.stop_crafting()
        show_message("🛑 Бот остановлен")

    def get_stats(self):
        """Возвращает статистику всех компонентов"""
        stats = {
            'bot': {
                'running': self.running,
                'config_loaded': bool(self.config)
            }
        }

        if self.controller:
            stats['controller'] = self.controller.get_stats()
        if self.scanner:
            stats['scanner'] = self.scanner.get_stats()
        if self.analyzer:
            stats['analyzer'] = self.analyzer.get_stats()

        return stats

    def emergency_stop(self):
        """Экстренная остановка"""
        if self.safety:
            self.safety.trigger_emergency_stop("Ручная остановка")
        self.stop_crafting()

    def start_mass_craft(self, currency_pos, target_mods, max_attempts_per_item=50):
        """Запускает массовый крафт"""
        try:
            show_message(f"🤖 Запуск массового крафта для {len(self.controller.item_slots)} предметов")

            if not hasattr(self.controller, 'start_mass_craft'):
                show_message("❌ Контроллер не поддерживает массовый крафт")
                return False

            # Запускаем массовый крафт через контроллер
            return self.controller.start_mass_craft(
                currency_pos=currency_pos,
                target_mods=target_mods,
                max_attempts_per_item=max_attempts_per_item
            )

        except Exception as e:
            show_message(f"❌ Ошибка запуска массового крафта: {e}")
            return False
