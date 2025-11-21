import json
import os
from dataclasses import dataclass


@dataclass
class CraftConfig:
    # Позиции элементов
    currency_position: tuple = None  # (x, y) Orb of Alteration
    item_position: tuple = None  # (x, y) предмет для крафта
    scan_region: tuple = None  # (x, y, width, height) область текста

    # Целевые моды
    target_mods: list = None
    stop_on_any_good_mod: bool = True

    # Настройки безопасности
    min_delay: float = 0.3
    max_delay: float = 0.5
    max_attempts: int = 1000
    click_variance: int = 15

    # Настройки OCR
    confidence_threshold: float = 0.7
    language: str = 'eng'


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = CraftConfig()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.config = CraftConfig(**data)
        return self.config

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config.__dict__, f, indent=4)
