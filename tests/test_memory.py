from src.core.memory import BankMemoryManager


def test_allocate_and_free():
    mem = BankMemoryManager(total_frames=8)
    assert mem.allocate(1, 2) is True
    assert mem.allocate(2, 2) is True
    assert mem.free_frames == 4
    assert mem.allocate(3, 5) is False
    assert mem.page_faults == 1
    freed = mem.free(1)
    assert freed == 2
    assert mem.allocate(3, 2) is True
    assert mem.free_frames == 4


def test_memory_map():
    mem = BankMemoryManager(total_frames=4)
    mem.allocate(10, 2)
    occupied = [f for f in mem.get_map() if f["pid"] == 10]
    assert len(occupied) == 2


def test_memory_pressure_unblock_scenario():
    mem = BankMemoryManager(total_frames=6)
    assert mem.allocate(1, 2) is True
    assert mem.allocate(2, 2) is True
    assert mem.allocate(3, 2) is True
    assert mem.allocate(4, 2) is False
    mem.free(1)
    assert mem.allocate(4, 2) is True
