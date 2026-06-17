from pathlib import Path
import tempfile

from src.concurrency.sync_primitives import run_log_race_demo


def test_log_race_safe_produces_correct_line_count():
    result = run_log_race_demo(num_threads=3, lines_per_thread=20, use_mutex=True)
    assert result["correct"] is True
    assert result["actual_lines"] == 60


def test_log_race_unsafe_may_lose_lines():
    result = run_log_race_demo(num_threads=4, lines_per_thread=100, use_mutex=False)
    assert result["protected"] is False
    assert result["actual_lines"] <= result["expected_lines"]
