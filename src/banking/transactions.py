from dataclasses import dataclass
from enum import Enum
from time import time


class TransactionType(Enum):
    TRANSFER = "Transferencia"
    WITHDRAW = "Saque"
    DEPOSIT = "Deposito"
    LOAN_PAYMENT = "PagamentoEmprestimo"
    FRAUD_CHECK = "Antifraude"
    STATEMENT = "Extrato"


@dataclass
class Transaction:
    tx_id: int
    tx_type: TransactionType
    source_account: int | None
    target_account: int | None
    amount: float
    priority_label: str = "NORMAL"
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time()

    def describe(self) -> str:
        if self.tx_type == TransactionType.TRANSFER:
            return (
                f"Transferencia {self.amount:.2f}: "
                f"conta {self.source_account} -> conta {self.target_account}"
            )
        if self.tx_type == TransactionType.WITHDRAW:
            return f"Saque {self.amount:.2f} da conta {self.source_account}"
        if self.tx_type == TransactionType.DEPOSIT:
            return f"Deposito {self.amount:.2f} na conta {self.target_account}"
        return f"{self.tx_type.value} (conta {self.source_account or self.target_account})"
