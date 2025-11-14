import json
import statistics
from datetime import datetime


class CraftAnalyzer:
    def __init__(self):
        self.craft_history = []
        self.session_start = datetime.now()

    def record_craft(self, attempt, mods_found, target_mod_found, currency_used="orb_of_alteration"):
        """Записывает результат крафта"""
        craft_data = {
            'timestamp': datetime.now().isoformat(),
            'attempt': attempt,
            'mods_found': mods_found,
            'target_mod_found': target_mod_found,
            'currency_used': currency_used,
            'mods_count': len(mods_found)
        }

        self.craft_history.append(craft_data)

        # Автосохранение каждые 10 записей
        if len(self.craft_history) % 10 == 0:
            self.save_stats()

    def get_stats(self):
        """Возвращает статистику крафта"""
        if not self.craft_history:
            return {}

        successful_crafts = [c for c in self.craft_history if c['target_mod_found']]
        total_attempts = len(self.craft_history)
        success_rate = len(successful_crafts) / total_attempts if total_attempts > 0 else 0

        mods_per_craft = [c['mods_count'] for c in self.craft_history]

        return {
            'total_attempts': total_attempts,
            'successful_crafts': len(successful_crafts),
            'success_rate': round(success_rate * 100, 2),
            'avg_mods_per_item': round(statistics.mean(mods_per_craft), 2) if mods_per_craft else 0,
            'session_duration': str(datetime.now() - self.session_start),
            'currency_used': {
                'orb_of_alteration': len([c for c in self.craft_history if c['currency_used'] == 'orb_of_alteration'])
            }
        }

    def save_stats(self):
        """Сохраняет статистику в файл"""
        stats = {
            'session_start': self.session_start.isoformat(),
            'craft_history': self.craft_history,
            'summary': self.get_stats()
        }

        with open('craft_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

    def print_real_time_stats(self):
        """Выводит реальную статистику"""
        stats = self.get_stats()
        if not stats:
            print("📊 Статистика: пока нет данных")
            return

        print(f"""
📊 СТАТИСТИКА КРАФТА:
├── Попыток: {stats['total_attempts']}
├── Успешных: {stats['successful_crafts']}
├── Процент успеха: {stats['success_rate']}%
├── Среднее модов: {stats['avg_mods_per_item']}
├── Orb of Alteration: {stats['currency_used']['orb_of_alteration']}
└── Длительность: {stats['session_duration']}
        """)
