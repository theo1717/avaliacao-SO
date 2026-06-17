import threading
from dataclasses import dataclass, field


@dataclass
class AccountLockManager:
    """Controla exclusao mutua de contas bancarias entre processos."""

    _holders: dict[int, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def try_acquire(self, account_id: int, pid: int) -> bool:
        with self._lock:
            holder = self._holders.get(account_id)
            if holder is None or holder == pid:
                self._holders[account_id] = pid
                return True
            return False

    def release(self, account_id: int, pid: int) -> None:
        with self._lock:
            if self._holders.get(account_id) == pid:
                del self._holders[account_id]

    def release_all_for_process(self, pid: int) -> list[int]:
        released: list[int] = []
        with self._lock:
            for acc_id, holder in list(self._holders.items()):
                if holder == pid:
                    del self._holders[acc_id]
                    released.append(acc_id)
        return released

    def get_holder(self, account_id: int) -> int | None:
        with self._lock:
            return self._holders.get(account_id)

    def snapshot(self) -> dict[int, int]:
        with self._lock:
            return dict(self._holders)
