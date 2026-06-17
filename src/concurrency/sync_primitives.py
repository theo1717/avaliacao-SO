import threading
from pathlib import Path


class BankMutex:
    """Encapsula threading.Lock para proteger regioes criticas do banco."""

    def __init__(self, name: str = "mutex") -> None:
        self.name = name
        self._lock = threading.Lock()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        if timeout >= 0:
            return self._lock.acquire(blocking=blocking, timeout=timeout)
        return self._lock.acquire(blocking=blocking)

    def release(self) -> None:
        self._lock.release()

    def __enter__(self) -> "BankMutex":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()


class BankSemaphore:
    """Encapsula threading.Semaphore para controlar acesso a recursos limitados."""

    def __init__(self, value: int, name: str = "semaphore") -> None:
        self.name = name
        self._semaphore = threading.Semaphore(value)

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        if timeout >= 0:
            return self._semaphore.acquire(blocking=blocking, timeout=timeout)
        return self._semaphore.acquire(blocking=blocking)

    def release(self) -> None:
        self._semaphore.release()


class SharedBalance:
    """Saldo compartilhado para demonstrar condicao de corrida."""

    def __init__(self, initial: float = 1000.0) -> None:
        self.balance = initial
        self.mutex = BankMutex("saldo")

    def deposit_unsafe(self, amount: float, iterations: int = 100) -> None:
        for _ in range(iterations):
            temp = self.balance
            temp += amount
            self.balance = temp

    def deposit_safe(self, amount: float, iterations: int = 100) -> None:
        for _ in range(iterations):
            with self.mutex:
                temp = self.balance
                temp += amount
                self.balance = temp


class TransactionLog:
    """Log compartilhado com escrita concorrente protegida por mutex."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.mutex = BankMutex("log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def append_unsafe(self, message: str) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def append_safe(self, message: str) -> None:
        with self.mutex:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(message + "\n")


def run_log_race_demo(
    num_threads: int = 4,
    lines_per_thread: int = 50,
    use_mutex: bool = False,
) -> dict:
    """Demonstra escrita concorrente em log com/sem mutex."""
    import tempfile

    log_path = Path(tempfile.gettempdir()) / "bank_log_race_test.log"
    tx_log = TransactionLog(log_path)
    expected_lines = num_threads * lines_per_thread
    threads: list[threading.Thread] = []

    def worker(tid: int) -> None:
        for i in range(lines_per_thread):
            msg = f"thread-{tid}-line-{i}"
            if use_mutex:
                tx_log.append_safe(msg)
            else:
                tx_log.append_unsafe(msg)

    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i + 1,), name=f"Logger-{i+1}")
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    actual_lines = len(log_path.read_text(encoding="utf-8").splitlines())
    return {
        "expected_lines": expected_lines,
        "actual_lines": actual_lines,
        "correct": actual_lines == expected_lines,
        "protected": use_mutex,
        "threads": num_threads,
        "lines_per_thread": lines_per_thread,
        "log_path": str(log_path),
    }


def run_race_condition_demo(
    num_threads: int = 4,
    iterations: int = 100,
    use_mutex: bool = False,
) -> dict:
    """Demonstra condicao de corrida com/sem mutex."""
    shared = SharedBalance(0.0)
    expected = num_threads * iterations * 1.0
    threads: list[threading.Thread] = []

    def worker() -> None:
        if use_mutex:
            shared.deposit_safe(1.0, iterations)
        else:
            shared.deposit_unsafe(1.0, iterations)

    for i in range(num_threads):
        t = threading.Thread(target=worker, name=f"ATM-{i+1}")
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return {
        "expected_balance": expected,
        "actual_balance": shared.balance,
        "correct": abs(shared.balance - expected) < 0.01,
        "protected": use_mutex,
        "threads": num_threads,
        "iterations_per_thread": iterations,
    }
