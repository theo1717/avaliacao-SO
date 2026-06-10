from src.concurrency.deadlock import DeadlockDemo


def test_deadlock_without_prevention_detected():
    demo = DeadlockDemo()
    result = demo.run_deadlock_scenario(use_prevention=False)
    assert result["deadlock_detected"] or result["completed_transfers"] < 2


def test_deadlock_with_prevention_completes():
    demo = DeadlockDemo()
    result = demo.run_deadlock_scenario(use_prevention=True)
    assert result["prevention_enabled"] is True
    assert result["deadlock_detected"] is False
    assert result["completed_transfers"] == 2
    assert result["balance_conserved"] is True
