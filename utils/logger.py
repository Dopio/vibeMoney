import logging
import os
from datetime import datetime


def setup_logger():
    """Настройка системы логирования"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f'logs/craft_bot_{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)


class CraftLogger:
    def __init__(self):
        self.logger = setup_logger()
        self.session_start = datetime.now()

    def log_craft_attempt(self, attempt, mods_found, success):
        self.logger.info(f"Попытка {attempt}: Моды {mods_found} - {'УСПЕХ' if success else 'продолжаем'}")

    def log_currency_used(self, currency_type, count):
        self.logger.info(f"Использовано {currency_type}: {count}")

    def log_session_summary(self, total_attempts, successful_crafts):
        duration = datetime.now() - self.session_start
        self.logger.info(
            f"Сессия завершена: "
            f"{total_attempts} попыток, "
            f"{successful_crafts} успешных, "
            f"длительность: {duration}")
