import sys
import os
import time
from core.safety import SafetyManager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_safety():
    print("=== Тестирование SafetyManager ===")
    print("=" * 40)

    safety = SafetyManager()

    # Тест 1: Нормальные действия
    print("\n1. Тест нормальных действий...")
    for i in range(5):
        safety.record_action(success=True, action_type=f"normal_action_{i}")
        safety.human_delay(0.5, 1.0)

    safety.print_safety_status()

    # Тест 2: Имитация ошибок
    print("\n2. Тест ошибок...")
    for i in range(8):
        safety.record_action(success=False, action_type=f"error_{i}")
        time.sleep(0.3)

    safety.print_safety_status()


if __name__ == "__main__":
    test_basic_safety()
