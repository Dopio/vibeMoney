import time
import random
import platform
from datetime import datetime


class SafetyManager:
    def __init__(self):
        self.start_time = time.time()
        self.last_action_time = time.time()
        self.consecutive_failures = 0
        self.total_actions = 0
        self.emergency_stop = False

        # Настройки безопасности
        self.safety_config = {
            'max_failures': 15,  # Максимум ошибок подряд
            'max_session_minutes': 120,  # Максимальная длительность сессии
            'min_action_interval': 0.2,  # Минимальный интервал между действиями
            'max_actions_per_minute': 180,  # Максимум действий в минуту
            'emergency_cooldown': 60,  # Перерыв после аварийной остановки (сек)
        }

        # Статистика
        self.actions_log = []
        self.failure_log = []

        print("✅ SafetyManager инициализирован (упрощенная версия)")

    def check_all_safety_conditions(self):
        """Проверяет все условия безопасности"""
        checks = [
            self.check_emergency_stop(),
            self.check_consecutive_failures(),
            self.check_session_duration(),
            self.check_action_frequency(),
        ]

        # Если хотя бы одна проверка не пройдена
        for check_name, passed, message in checks:
            if not passed:
                print(f"🚨 Безопасность: {check_name} - {message}")
                return False

        return True

    def check_emergency_stop(self):
        """Проверка аварийной остановки"""
        if self.emergency_stop:
            cooldown_passed = (time.time() - self.last_action_time) > self.safety_config['emergency_cooldown']
            if cooldown_passed:
                self.emergency_stop = False
                self.consecutive_failures = 0
                return ("Emergency Stop", True, "Коулдаун завершен")
            else:
                remaining = self.safety_config['emergency_cooldown'] - (time.time() - self.last_action_time)
                return ("Emergency Stop", False, f"Аварийная остановка ({remaining:.0f}с осталось)")
        return ("Emergency Stop", True, "OK")

    def check_consecutive_failures(self):
        """Проверка количества последовательных ошибок"""
        if self.consecutive_failures >= self.safety_config['max_failures']:
            self.trigger_emergency_stop("Слишком много ошибок подряд")
            return ("Consecutive Failures", False, f"Слишком много ошибок: {self.consecutive_failures}")
        return ("Consecutive Failures", True, f"OK ({self.consecutive_failures}/{self.safety_config['max_failures']})")

    def check_session_duration(self):
        """Проверка длительности сессии"""
        session_duration = (time.time() - self.start_time) / 60  # в минутах
        if session_duration > self.safety_config['max_session_minutes']:
            return ("Session Duration", False, f"Сессия слишком долгая: {session_duration:.1f} мин")
        return (
        "Session Duration", True, f"OK ({session_duration:.1f}/{self.safety_config['max_session_minutes']} мин)")

    def check_action_frequency(self):
        """Проверка частоты действий"""
        current_time = time.time()

        # Проверка минимального интервала
        time_since_last_action = current_time - self.last_action_time
        if time_since_last_action < self.safety_config['min_action_interval']:
            return ("Action Frequency", False, f"Слишком частые действия: {time_since_last_action:.2f}с")

        # Проверка действий в минуту
        recent_actions = [t for t in self.actions_log if t > current_time - 60]
        if len(recent_actions) > self.safety_config['max_actions_per_minute']:
            return ("Actions Per Minute", False, f"Слишком много действий: {len(recent_actions)}/мин")

        return ("Action Frequency", True, "OK")

    def record_action(self, success=True, action_type="unknown"):
        """Записывает действие в лог"""
        current_time = time.time()
        self.actions_log.append(current_time)
        self.last_action_time = current_time
        self.total_actions += 1

        if not success:
            self.consecutive_failures += 1
            self.failure_log.append({
                'time': current_time,
                'type': action_type,
                'consecutive_failures': self.consecutive_failures
            })
            print(f"⚠️ Зарегистрирована ошибка: {action_type} (подряд: {self.consecutive_failures})")
        else:
            self.consecutive_failures = 0

    def trigger_emergency_stop(self, reason="Неизвестная причина"):
        """Аварийная остановка"""
        self.emergency_stop = True
        print(f"🚨 АВАРИЙНАЯ ОСТАНОВКА: {reason}")
        self.log_emergency_stop(reason)

    def log_emergency_stop(self, reason):
        """Логирование аварийной остановки"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'total_actions': self.total_actions,
            'session_duration_minutes': (time.time() - self.start_time) / 60,
            'consecutive_failures': self.consecutive_failures
        }

        # Сохраняем в файл
        try:
            with open('safety_log.json', 'a') as f:
                f.write(f"{log_entry}\n")
        except Exception as e:
            print(f"⚠️ Не удалось записать лог безопасности: {e}")

    def get_safety_report(self):
        """Возвращает отчет о безопасности"""
        session_duration = (time.time() - self.start_time) / 60
        recent_actions = [t for t in self.actions_log if t > time.time() - 60]

        report = {
            'session_duration_minutes': round(session_duration, 1),
            'total_actions': self.total_actions,
            'consecutive_failures': self.consecutive_failures,
            'emergency_stop_active': self.emergency_stop,
            'actions_per_minute': len(recent_actions),
            'safety_checks_passed': self.check_all_safety_conditions(),
            'system': platform.system()
        }

        return report

    def human_delay(self, min_seconds=0.5, max_seconds=2.0):
        """Случайная задержка с проверкой безопасности"""
        delay = random.uniform(min_seconds, max_seconds)

        # Разбиваем задержку на части для возможности прерывания
        step = 0.1
        remaining = delay

        while remaining > 0 and not self.emergency_stop:
            sleep_time = min(step, remaining)
            time.sleep(sleep_time)
            remaining -= sleep_time

            # Периодически проверяем безопасность
            if remaining > 0 and not self.check_all_safety_conditions():
                break

        return remaining == 0  # Возвращает True если задержка завершена полностью

    def print_safety_status(self):
        """Выводит текущий статус безопасности"""
        report = self.get_safety_report()
        print("\n📊 Статус безопасности:")
        print(f"   Длительность сессии: {report['session_duration_minutes']} мин")
        print(f"   Всего действий: {report['total_actions']}")
        print(f"   Ошибок подряд: {report['consecutive_failures']}")
        print(f"   Действий в минуту: {report['actions_per_minute']}")
        print(f"   Аварийная остановка: {'АКТИВНА' if report['emergency_stop_active'] else 'не активна'}")
        print(f"   Проверки пройдены: {'✅' if report['safety_checks_passed'] else '❌'}")