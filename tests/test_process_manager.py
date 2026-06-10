from src.core.process import Priority, ProcessState
from src.core.process_manager import ProcessManager


def test_create_and_admit_process():
    pm = ProcessManager()
    pcb = pm.create_process("Test", Priority.NORMAL, burst_time=5, arrival_time=0)
    assert pcb.pid == 1
    assert pcb.state == ProcessState.NEW
    pm.admit_process(pcb.pid)
    assert pcb.state == ProcessState.READY
    assert pcb.pid in pm.ready_queue


def test_block_and_unblock():
    pm = ProcessManager()
    pcb = pm.create_process("Test", Priority.VIP, burst_time=3)
    pm.admit_process(pcb.pid)
    pm.block_process(pcb.pid)
    assert pcb.state == ProcessState.BLOCKED
    assert pcb.pid in pm.blocked_queue
    assert pcb.pid not in pm.ready_queue
    pm.unblock_process(pcb.pid)
    assert pcb.state == ProcessState.READY
    assert pcb.pid in pm.ready_queue


def test_terminate_process():
    pm = ProcessManager()
    pcb = pm.create_process("Test", Priority.BATCH, burst_time=2)
    pm.admit_process(pcb.pid)
    pm.terminate_process(pcb.pid)
    assert pcb.state == ProcessState.TERMINATED
    assert pcb.pid in pm.terminated


def test_set_priority():
    pm = ProcessManager()
    pcb = pm.create_process("Test", Priority.BATCH, burst_time=2)
    pm.set_priority(pcb.pid, Priority.VIP)
    assert pcb.priority == Priority.VIP
