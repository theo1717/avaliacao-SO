import threading
import time
from dataclasses import dataclass, field

from src.banking.accounts import Account, AccountRegistry


@dataclass
class DeadlockDemo:
    registry: AccountRegistry = field(default_factory=AccountRegistry)
    deadlock_detected: bool = False
    completed_transfers: int = 0
    _log: list[str] = field(default_factory=list)
    _log_lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        if not self.registry.accounts:
            self.registry.setup_default_accounts()

    def _log_msg(self, msg: str) -> None:
        with self._log_lock:
            self._log.append(msg)

    def _transfer_unsafe(
        self,
        from_id: int,
        to_id: int,
        amount: float,
        thread_name: str,
    ) -> bool:
        """Transferencia sem ordenacao de locks - pode causar deadlock."""
        from_acc = self.registry.get(from_id)
        to_acc = self.registry.get(to_id)

        self._log_msg(f"[{thread_name}] Tentando lock conta {from_id}")
        if not from_acc.get_lock().acquire(timeout=3):
            self.deadlock_detected = True
            self._log_msg(f"[{thread_name}] DEADLOCK: timeout ao lockar conta {from_id}")
            return False

        time.sleep(0.1)
        self._log_msg(f"[{thread_name}] Lock conta {from_id} OK, tentando conta {to_id}")

        if not to_acc.get_lock().acquire(timeout=3):
            self.deadlock_detected = True
            self._log_msg(f"[{thread_name}] DEADLOCK: timeout ao lockar conta {to_id}")
            from_acc.get_lock().release()
            return False

        try:
            if from_acc.balance >= amount:
                from_acc.balance -= amount
                to_acc.balance += amount
                self.completed_transfers += 1
                self._log_msg(
                    f"[{thread_name}] Transferiu {amount} de {from_id} para {to_id}"
                )
            return True
        finally:
            to_acc.get_lock().release()
            from_acc.get_lock().release()

    def _transfer_safe(
        self,
        from_id: int,
        to_id: int,
        amount: float,
        thread_name: str,
    ) -> bool:
        """Prevencao por ordenacao de recursos: menor ID primeiro."""
        first_id, second_id = sorted([from_id, to_id])
        first_acc = self.registry.get(first_id)
        second_acc = self.registry.get(second_id)
        from_acc = self.registry.get(from_id)
        to_acc = self.registry.get(to_id)

        self._log_msg(
            f"[{thread_name}] Lock ordenado: {first_id} depois {second_id}"
        )

        with first_acc.get_lock():
            with second_acc.get_lock():
                if from_acc.balance >= amount:
                    from_acc.balance -= amount
                    to_acc.balance += amount
                    self.completed_transfers += 1
                    self._log_msg(
                        f"[{thread_name}] Transferiu {amount} de {from_id} para {to_id}"
                    )
                return True
        return False

    def run_deadlock_scenario(self, use_prevention: bool = False) -> dict:
        self.deadlock_detected = False
        self.completed_transfers = 0
        self._log.clear()

        acc_a = self.registry.get(1)
        acc_b = self.registry.get(2)
        initial_a = acc_a.balance
        initial_b = acc_b.balance

        transfer_fn = self._transfer_safe if use_prevention else self._transfer_unsafe

        t1 = threading.Thread(
            target=transfer_fn,
            args=(1, 2, 100.0, "Thread-A->B"),
            name="Transfer-A-B",
        )
        t2 = threading.Thread(
            target=transfer_fn,
            args=(2, 1, 150.0, "Thread-B->A"),
            name="Transfer-B-A",
        )

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        return {
            "prevention_enabled": use_prevention,
            "deadlock_detected": self.deadlock_detected,
            "completed_transfers": self.completed_transfers,
            "final_balances": {
                acc_a.account_id: acc_a.balance,
                acc_b.account_id: acc_b.balance,
            },
            "balance_conserved": abs(
                (acc_a.balance + acc_b.balance) - (initial_a + initial_b)
            ) < 0.01,
            "log": list(self._log),
        }
