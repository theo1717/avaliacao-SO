import random

from src.core.process import PCB, Priority
from src.core.process_manager import ProcessManager
from src.banking.transactions import TransactionType


BURST_BY_OPERATION = {
    TransactionType.TRANSFER: (3, 6),
    TransactionType.WITHDRAW: (2, 4),
    TransactionType.DEPOSIT: (2, 4),
    TransactionType.LOAN_PAYMENT: (4, 7),
    TransactionType.FRAUD_CHECK: (5, 8),
    TransactionType.STATEMENT: (1, 3),
}

PRIORITY_BY_OPERATION = {
    TransactionType.TRANSFER: Priority.NORMAL,
    TransactionType.WITHDRAW: Priority.VIP,
    TransactionType.DEPOSIT: Priority.NORMAL,
    TransactionType.LOAN_PAYMENT: Priority.VIP,
    TransactionType.FRAUD_CHECK: Priority.BATCH,
    TransactionType.STATEMENT: Priority.BATCH,
}


class BankingOperationFactory:
    @staticmethod
    def random_priority() -> Priority:
        return random.choices(
            [Priority.VIP, Priority.NORMAL, Priority.BATCH],
            weights=[2, 5, 3],
        )[0]

    @staticmethod
    def create_process_from_operation(
        pm: ProcessManager,
        tx_type: TransactionType,
        arrival_time: int = 0,
        quantum: int = 2,
        priority: Priority | None = None,
    ) -> PCB:
        low, high = BURST_BY_OPERATION[tx_type]
        burst = random.randint(low, high)
        prio = priority or PRIORITY_BY_OPERATION[tx_type]
        return pm.create_process(
            name=f"{tx_type.value}-{pm._next_pid}",
            priority=prio,
            burst_time=burst,
            arrival_time=arrival_time,
            quantum=quantum,
            operation_type=tx_type.value,
        )

    @staticmethod
    def generate_banking_workload(
        pm: ProcessManager,
        count: int,
        quantum: int = 2,
        current_tick: int = 0,
    ) -> list[PCB]:
        created: list[PCB] = []
        types = list(TransactionType)
        for _ in range(count):
            tx_type = random.choice(types)
            arrival = current_tick + random.randint(0, 3)
            pcb = BankingOperationFactory.create_process_from_operation(
                pm, tx_type, arrival_time=arrival, quantum=quantum
            )
            if arrival == current_tick:
                pm.admit_process(pcb.pid)
            created.append(pcb)
        return created
