from dataclasses import dataclass, field
from enum import Enum, IntEnum


class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"


class Priority(IntEnum):
    VIP = 0
    NORMAL = 1
    BATCH = 2


@dataclass
class PCB:
    pid: int
    name: str
    priority: Priority
    burst_time: int
    remaining_time: int
    state: ProcessState = ProcessState.NEW
    quantum: int = 2
    deadline: int = 0
    arrival_time: int = 0
    start_time: int | None = None
    finish_time: int | None = None
    waiting_time: int = 0
    last_scheduled_tick: int | None = None
    operation_type: str = "operacao"
    pages_required: int = 1
    account_id: int = 1
    block_reason: str = ""
    deadline_missed: bool = False

    def __post_init__(self) -> None:
        if self.deadline == 0:
            self.deadline = self.arrival_time + self.burst_time * 2

    @property
    def response_time(self) -> int | None:
        if self.start_time is None:
            return None
        return self.start_time - self.arrival_time

    @property
    def turnaround_time(self) -> int | None:
        if self.finish_time is None:
            return None
        return self.finish_time - self.arrival_time

    def to_dict(self) -> dict:
        return {
            "pid": self.pid,
            "name": self.name,
            "operation": self.operation_type,
            "priority": self.priority.name,
            "state": self.state.value,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "quantum": self.quantum,
            "deadline": self.deadline,
            "waiting_time": self.waiting_time,
            "response_time": self.response_time,
            "turnaround_time": self.turnaround_time,
            "pages_required": self.pages_required,
            "account_id": self.account_id,
            "block_reason": self.block_reason,
            "deadline_missed": self.deadline_missed,
        }

    def needs_account_lock(self) -> bool:
        return self.operation_type in (
            "Transferencia",
            "Saque",
            "Deposito",
            "PagamentoEmprestimo",
        )
