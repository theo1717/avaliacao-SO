from src.core.metrics import SimulationMetrics
from src.core.process import Priority, ProcessState
from src.core.process_manager import ProcessManager
from src.core.scheduler import EDFScheduler, PriorityScheduler, RoundRobinScheduler


def _setup_pm_with_processes(quantum: int = 2) -> ProcessManager:
    pm = ProcessManager()
    for i, (prio, burst) in enumerate(
        [(Priority.NORMAL, 4), (Priority.VIP, 3), (Priority.BATCH, 2)]
    ):
        pcb = pm.create_process(f"P{i}", prio, burst, arrival_time=0, quantum=quantum)
        pm.admit_process(pcb.pid)
    return pm


def test_round_robin_respects_quantum():
    pm = _setup_pm_with_processes(quantum=2)
    metrics = SimulationMetrics()
    scheduler = RoundRobinScheduler(pm, metrics, quantum=2)

    ticks = 0
    max_ticks = 30
    while ticks < max_ticks:
        if not scheduler.tick(ticks):
            break
        ticks += 1

    completed = metrics.completed
    assert len(completed) == 3
    assert all(p.state == ProcessState.TERMINATED for p in completed)


def test_priority_executes_vip_first():
    pm = ProcessManager()
    normal = pm.create_process("Normal", Priority.NORMAL, 5, arrival_time=0)
    vip = pm.create_process("VIP", Priority.VIP, 5, arrival_time=0)
    pm.admit_process(normal.pid)
    pm.admit_process(vip.pid)

    metrics = SimulationMetrics()
    scheduler = PriorityScheduler(pm, metrics)

    scheduler.tick(0)
    assert scheduler.current_process is not None
    assert scheduler.current_process.pid == vip.pid


def test_priority_completes_all_processes():
    pm = _setup_pm_with_processes()
    metrics = SimulationMetrics()
    scheduler = PriorityScheduler(pm, metrics)

    ticks = 0
    while ticks < 30:
        if not scheduler.tick(ticks):
            active = pm.get_active_processes()
            if all(p.state == ProcessState.TERMINATED for p in active):
                break
        ticks += 1

    assert len(metrics.completed) == 3


def test_edf_executes_earliest_deadline_first():
    pm = ProcessManager()
    late = pm.create_process(
        "Late", Priority.BATCH, 4, arrival_time=0, deadline=20
    )
    early = pm.create_process(
        "Early", Priority.BATCH, 4, arrival_time=0, deadline=8
    )
    pm.admit_process(late.pid)
    pm.admit_process(early.pid)

    metrics = SimulationMetrics()
    scheduler = EDFScheduler(pm, metrics)
    scheduler.tick(0)
    assert scheduler.current_process is not None
    assert scheduler.current_process.pid == early.pid
