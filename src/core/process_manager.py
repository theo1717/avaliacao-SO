import random

from src.core.process import PCB, Priority, ProcessState

OPERATION_TYPES = [
    "Transferencia",
    "Saque",
    "Deposito",
    "PagamentoEmprestimo",
    "Antifraude",
    "Extrato",
]


class ProcessManager:
    def __init__(self) -> None:
        self._next_pid = 1
        self.processes: dict[int, PCB] = {}
        self.ready_queue: list[int] = []
        self.blocked_queue: list[int] = []
        self.terminated: list[int] = []

    def create_process(
        self,
        name: str,
        priority: Priority,
        burst_time: int,
        arrival_time: int = 0,
        quantum: int = 2,
        operation_type: str = "operacao",
        deadline: int = 0,
    ) -> PCB:
        pcb = PCB(
            pid=self._next_pid,
            name=name,
            priority=priority,
            burst_time=burst_time,
            remaining_time=burst_time,
            state=ProcessState.NEW,
            quantum=quantum,
            deadline=deadline,
            arrival_time=arrival_time,
            operation_type=operation_type,
        )
        self.processes[pcb.pid] = pcb
        self._next_pid += 1
        return pcb

    def admit_process(self, pid: int) -> None:
        pcb = self.processes[pid]
        pcb.state = ProcessState.READY
        self.ready_queue.append(pid)

    def terminate_process(self, pid: int) -> None:
        pcb = self.processes[pid]
        pcb.state = ProcessState.TERMINATED
        if pid in self.ready_queue:
            self.ready_queue.remove(pid)
        if pid in self.blocked_queue:
            self.blocked_queue.remove(pid)
        if pid not in self.terminated:
            self.terminated.append(pid)

    def block_process(self, pid: int) -> None:
        pcb = self.processes[pid]
        pcb.state = ProcessState.BLOCKED
        if pid in self.ready_queue:
            self.ready_queue.remove(pid)
        if pid not in self.blocked_queue:
            self.blocked_queue.append(pid)

    def unblock_process(self, pid: int) -> None:
        pcb = self.processes[pid]
        pcb.state = ProcessState.READY
        if pid in self.blocked_queue:
            self.blocked_queue.remove(pid)
        if pid not in self.ready_queue:
            self.ready_queue.append(pid)

    def set_priority(self, pid: int, priority: Priority) -> None:
        self.processes[pid].priority = priority

    def set_state(self, pid: int, state: ProcessState) -> None:
        self.processes[pid].state = state

    def get_process(self, pid: int) -> PCB:
        return self.processes[pid]

    def get_active_processes(self) -> list[PCB]:
        return [
            p
            for p in self.processes.values()
            if p.state != ProcessState.TERMINATED
        ]

    def generate_random_processes(
        self,
        count: int,
        quantum: int = 2,
        arrival_spread: int = 3,
        current_tick: int = 0,
    ) -> list[PCB]:
        created: list[PCB] = []
        for i in range(count):
            priority = random.choices(
                [Priority.VIP, Priority.NORMAL, Priority.BATCH],
                weights=[2, 5, 3],
            )[0]
            burst = random.randint(2, 8)
            arrival = current_tick + random.randint(0, arrival_spread)
            op = random.choice(OPERATION_TYPES)
            pcb = self.create_process(
                name=f"Proc-{self._next_pid}",
                priority=priority,
                burst_time=burst,
                arrival_time=arrival,
                quantum=quantum,
                operation_type=op,
            )
            if arrival == current_tick:
                self.admit_process(pcb.pid)
            created.append(pcb)
        return created

    def admit_arrived(self, current_tick: int) -> list[int]:
        admitted: list[int] = []
        for pcb in self.processes.values():
            if (
                pcb.state == ProcessState.NEW
                and pcb.arrival_time <= current_tick
            ):
                self.admit_process(pcb.pid)
                admitted.append(pcb.pid)
        return admitted
