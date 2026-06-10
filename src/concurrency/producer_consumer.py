import threading
import time
from dataclasses import dataclass, field

from src.concurrency.sync_primitives import BankMutex, BankSemaphore
from src.banking.transactions import Transaction, TransactionType


@dataclass
class ProducerConsumerBuffer:
    """Buffer limitado com semaforos (padrao produtor-consumidor)."""

    capacity: int = 5
    _buffer: list[Transaction] = field(default_factory=list)
    _empty_slots: BankSemaphore = field(init=False)
    _filled_slots: BankSemaphore = field(init=False)
    _buffer_lock: BankMutex = field(init=False)
    _tx_counter: int = 0
    _produced: int = 0
    _consumed: int = 0
    _log: list[str] = field(default_factory=list)
    _log_lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self._empty_slots = BankSemaphore(self.capacity, "empty_slots")
        self._filled_slots = BankSemaphore(0, "filled_slots")
        self._buffer_lock = BankMutex("buffer")

    def _append_log(self, message: str) -> None:
        with self._log_lock:
            self._log.append(message)

    def produce(self, producer_id: int, tx_type: TransactionType, amount: float) -> bool:
        if not self._empty_slots.acquire(timeout=2):
            self._append_log(f"[ATM-{producer_id}] Buffer cheio - bloqueado")
            return False

        with self._buffer_lock:
            self._tx_counter += 1
            tx = Transaction(
                tx_id=self._tx_counter,
                tx_type=tx_type,
                source_account=1,
                target_account=2,
                amount=amount,
            )
            self._buffer.append(tx)
            self._produced += 1
            self._append_log(
                f"[ATM-{producer_id}] Produziu TX-{tx.tx_id} "
                f"({tx_type.value}) | buffer={len(self._buffer)}/{self.capacity}"
            )

        self._filled_slots.release()
        return True

    def consume(self, consumer_id: int) -> Transaction | None:
        if not self._filled_slots.acquire(timeout=2):
            self._append_log(f"[Backend-{consumer_id}] Buffer vazio - bloqueado")
            return None

        with self._buffer_lock:
            tx = self._buffer.pop(0)
            self._consumed += 1
            self._append_log(
                f"[Backend-{consumer_id}] Consumiu TX-{tx.tx_id} "
                f"({tx.tx_type.value}) | buffer={len(self._buffer)}/{self.capacity}"
            )

        self._empty_slots.release()
        return tx

    def get_log(self) -> list[str]:
        with self._log_lock:
            return list(self._log)

    def stats(self) -> dict:
        return {
            "produced": self._produced,
            "consumed": self._consumed,
            "buffer_size": len(self._buffer),
            "capacity": self.capacity,
        }


def run_producer_consumer_demo(
    num_producers: int = 2,
    num_consumers: int = 1,
    items_per_producer: int = 5,
    capacity: int = 3,
    delay: float = 0.05,
) -> dict:
    buffer = ProducerConsumerBuffer(capacity=capacity)
    threads: list[threading.Thread] = []
    tx_types = [TransactionType.DEPOSIT, TransactionType.WITHDRAW, TransactionType.TRANSFER]

    def producer(pid: int) -> None:
        for i in range(items_per_producer):
            tx_type = tx_types[i % len(tx_types)]
            buffer.produce(pid, tx_type, amount=100.0 + i * 10)
            time.sleep(delay)

    def consumer(cid: int) -> None:
        total = num_producers * items_per_producer
        consumed = 0
        while consumed < total:
            tx = buffer.consume(cid)
            if tx:
                consumed += 1
            time.sleep(delay * 1.5)

    for i in range(num_producers):
        t = threading.Thread(target=producer, args=(i + 1,), name=f"ATM-{i+1}")
        threads.append(t)
    for i in range(num_consumers):
        t = threading.Thread(target=consumer, args=(i + 1,), name=f"Backend-{i+1}")
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return {
        "stats": buffer.stats(),
        "log": buffer.get_log(),
    }
