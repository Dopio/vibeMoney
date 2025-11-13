import time
from core.safety import SafetyManager


def test_basic_safety():
    print("🧪 Тестирование SafetyManager (упрощенная версия)")
    print("=" * 50)

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

    # Тест 3: Аварийная остановка
    print("\n3. Тест аварийной остановки...")
    for i in range(5):
        safety.record_action(success=False, action_type=f"critical_error_{i}")

    safety_check = safety.check_all_safety_conditions()
    print(f"   Безопасность: {'✅' if safety_check else '❌'}")

    # Тест 4: Задержка с прерыванием
    print("\n4. Тест задержки...")
    print("   Запуск задержки 3 секунды (можно прервать Ctrl+C)")
    try:
        completed = safety.human_delay(3, 3)
        if completed:
            print("   ✅ Задержка завершена полностью")
        else:
            print("   ⏹️ Задержка прервана системой безопасности")
    except KeyboardInterrupt:
        print("   ⏹️ Задержка прервана пользователем")


def test_emergency_recovery():
    print("\n🔄 Тест восстановления после аварийной остановки")
    print("=" * 55)

    safety = SafetyManager()

    # Вызываем аварийную остановку
    print("Активация аварийной остановки...")
    for i in range(12):
        safety.record_action(success=False, action_type="emergency_trigger")

    safety.print_safety_status()

    # Ждем восстановления
    print("\nОжидание восстановления...")
    for i in range(10):
        time.sleep(1)
        safety_check = safety.check_all_safety_conditions()
        if safety_check:
            print(f"   ✅ Восстановлено через {i + 1} секунд")
            break
        else:
            print(f"   ⏳ Ожидание... {i + 1}/10с")

    safety.print_safety_status()


def test_performance_limits():
    print("\n📈 Тест ограничений производительности")
    print("=" * 45)

    safety = SafetyManager()

    # Быстрые действия
    print("Имитация быстрых действий...")
    start_time = time.time()
    action_count = 0

    while time.time() - start_time < 2:  # 2 секунды теста
        safety.record_action(success=True, action_type="fast_action")
        action_count += 1
        time.sleep(0.05)  # Очень быстрые действия

    safety.print_safety_status()
    print(f"   Выполнено действий: {action_count} за 2 секунды")


if __name__ == "__main__":
    test_basic_safety()
    test_emergency_recovery()
    test_performance_limits()

    print("\n🎉 Все тесты завершены!")
