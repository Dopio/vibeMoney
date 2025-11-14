import sys
import os
from core.analyzer import CraftAnalyzer
import random
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_crafting():
    """Демо-режим для тестирования без игры"""
    print("🎮 ДЕМО-РЕЖИМ: Имитация крафта")
    print("=" * 40)

    analyzer = CraftAnalyzer()

    # Имитируемые моды для тестирования
    sample_mods = [
        ["Increased Physical Damage", "Adds 5-10 Physical Damage"],
        ["+12 to Intelligence", "14% increased Stun Recovery"],
        ["Critical Strike Chance", "Attack Speed", "Added Fire Damage"],
        ["+31 to Maximum Life", "+24% to Cold Resistance"],
        ["Socketed Gems are Supported by Level 10 Faster Attacks"],
        ["Minions deal 15% increased Damage", "+1 to Level of Minion Gems"]
    ]

    target_mods = ["increased physical damage", "critical strike", "faster attacks"]

    for attempt in range(1, 21):
        print(f"\n♻️ Попытка {attempt}")

        # Имитация использования валюты
        time.sleep(1)

        # Случайные моды
        current_mods = random.choice(sample_mods)
        print(f"📄 Моды: {current_mods}")

        # Проверка на целевые моды
        found = any(any(target in mod.lower() for target in target_mods) for mod in current_mods)

        if found:
            print("🎉 ЦЕЛЕВОЙ МОД НАЙДЕН!")
            analyzer.record_craft(attempt, current_mods, True)
            break
        else:
            analyzer.record_craft(attempt, current_mods, False)

        # Показываем статистику каждые 5 попыток
        if attempt % 5 == 0:
            analyzer.print_real_time_stats()

    # Финальная статистика
    print("\n📊 ДЕМО ЗАВЕРШЕНО")
    analyzer.print_real_time_stats()


if __name__ == "__main__":
    demo_crafting()
