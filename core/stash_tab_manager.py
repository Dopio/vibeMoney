import time
from typing import Dict, Tuple, List, Optional

import pyautogui


class StashTabManager:
    """Управление вкладками и сеткой предметов"""

    def __init__(self):
        self.tab_positions: Dict[str, Tuple[int, int]] = {}  # 'crafting': (x, y)
        self.item_grid: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
        self.first_item_pos: Optional[Tuple[int, int]] = None
        self.grid_size: Tuple[int, int] = (12, 5)  # стандартный размер сетки POE
        self.item_spacing: Tuple[int, int] = (60, 60)  # расстояние между предметами

    def set_tab_position(self, tab_name: str, position: Tuple[int, int]):
        """Установить позицию вкладки"""
        self.tab_positions[tab_name] = position
        print(f"✅ Вкладка '{tab_name}': {position}")

    def set_item_grid(self, grid_region: Tuple[int, int, int, int]):
        """Установить область предметов внутри вкладки"""
        self.item_grid = grid_region
        print(f"✅ Область предметов: {grid_region}")

    def set_first_item_position(self, position: Tuple[int, int]):
        """Установить позицию первого предмета"""
        self.first_item_pos = position
        print(f"✅ Первый предмет: {position}")

    def calculate_item_slots(self) -> List[Tuple[int, int]]:
        """Вычислить все позиции предметов в сетке"""
        if not self.first_item_pos:
            raise ValueError("Не установлена позиция первого предмета")

        slots = []
        start_x, start_y = self.first_item_pos

        for row in range(self.grid_size[1]):  # rows
            for col in range(self.grid_size[0]):  # columns
                x = start_x + (col * self.item_spacing[0])
                y = start_y + (row * self.item_spacing[1])

                # Проверяем, что позиция внутри области предметов
                if self._is_position_in_grid(x, y):
                    slots.append((x, y))

        print(f"✅ Рассчитано {len(slots)} слотов предметов")
        return slots

    def _is_position_in_grid(self, x: int, y: int) -> bool:
        """Проверить, что позиция внутри области предметов"""
        if not self.item_grid:
            return True  # если область не задана, принимаем все позиции

        grid_x, grid_y, grid_w, grid_h = self.item_grid
        return (grid_x <= x <= grid_x + grid_w and
                grid_y <= y <= grid_y + grid_h)

    def switch_to_tab(self, tab_name: str):
        """Переключиться на указанную вкладку"""
        if tab_name not in self.tab_positions:
            raise ValueError(f"Вкладка '{tab_name}' не настроена")

        tab_x, tab_y = self.tab_positions[tab_name]
        pyautogui.click(tab_x, tab_y)
        time.sleep(0.3)  # ждем переключения вкладки
        print(f"🔁 Переключились на вкладку: {tab_name}")
