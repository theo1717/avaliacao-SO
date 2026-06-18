from src.concurrency.sync_primitives import run_race_condition_demo


def test_race_condition_safe_produces_expected_balance():
    result = run_race_condition_demo(num_threads=4, iterations=100, use_mutex=True)
    assert result["correct"] is True
    assert result["actual_balance"] == 400.0


def test_race_condition_unsafe_loses_updates():
    result = run_race_condition_demo(num_threads=4, iterations=100, use_mutex=False)
    assert result["protected"] is False
    assert result["correct"] is False
    assert result["actual_balance"] < result["expected_balance"]
