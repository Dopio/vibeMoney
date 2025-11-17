import sys
import os
from core.advanced_analyzer import AdvancedAnalyzer
from utils.poe_mod_generator import PoeModGenerator
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_advanced_demo():
    print("=== ПРОДВИНУТОЕ ДЕМО: Реалистичная имитация крафта ===")
    print("=" * 55)

    analyzer = AdvancedAnalyzer()
    mod_generator = PoeModGenerator()

    profiles = ["physical_weapon", "caster_weapon", "body_armour", "jewel"]

    total_attempts = 0
    for profile in profiles:
        print(f"\n--- Профиль: {profile} ---")

        session = mod_generator.generate_item_session(profile, random.randint(20, 40))

        for craft in session:
            total_attempts += 1

            print(f"Попытка {total_attempts}: {len(craft['mods'])} модов")
            for mod in craft['mods'][:2]:
                print(f"   {mod}")

            if craft['target_found']:
                print("   [УСПЕХ] Целевой мод найден!")

            analyzer.record_craft(
                attempt=total_attempts,
                mods_found=craft['mods'],
                target_mod_found=craft['target_found'],
                profile=profile
            )

            time.sleep(0.1)

            if craft['target_found']:
                break

    print("\n" + "=" * 55)
    print("ФИНАЛЬНЫЙ АНАЛИЗ")
    print("=" * 55)

    report = analyzer.generate_report()
    print(report)


if __name__ == "__main__":
    run_advanced_demo()
