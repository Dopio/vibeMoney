from utils.helpers import human_click, human_delay

class CraftController:
    def use_currency(self, currency_pos, item_pos):
        print(f"🖱️ Используем валюту: {currency_pos} -> {item_pos}")
        human_delay(0.5, 1.0)  # Заглушка