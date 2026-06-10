import threading
from dataclasses import dataclass, field


@dataclass
class Account:
    account_id: int
    holder: str
    balance: float = 1000.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def get_lock(self) -> threading.Lock:
        return self._lock


class AccountRegistry:
    def __init__(self) -> None:
        self.accounts: dict[int, Account] = {}
        self._next_id = 1
        self._registry_lock = threading.Lock()

    def create_account(self, holder: str, balance: float = 1000.0) -> Account:
        with self._registry_lock:
            account = Account(
                account_id=self._next_id,
                holder=holder,
                balance=balance,
            )
            self.accounts[account.account_id] = account
            self._next_id += 1
            return account

    def get(self, account_id: int) -> Account:
        return self.accounts[account_id]

    def setup_default_accounts(self) -> None:
        self.create_account("Alice", 1000.0)
        self.create_account("Bob", 1000.0)
        self.create_account("Carlos", 500.0)
