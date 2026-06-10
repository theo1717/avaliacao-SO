import random
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

from src.banking.operations import BankingOperationFactory
from src.concurrency.producer_consumer import ProducerConsumerBuffer
from src.concurrency.sync_primitives import BankMutex, TransactionLog
from src.core.metrics import SimulationMetrics
from src.core.process import ProcessState
from src.core.process_manager import ProcessManager
from src.core.scheduler import PriorityScheduler, RoundRobinScheduler, Scheduler


@dataclass
class SimulationConfig:
    quantum: int = 2
    num_processes: int = 8
    tick_delay: float = 0.1
    fast_mode: bool = False
    num_atm_threads: int = 2
    scheduler_type: str = "RR"
    block_probability: float = 0.05


@dataclass
class SimulationEngine:
    config: SimulationConfig = field(default_factory=SimulationConfig)
    process_manager: ProcessManager = field(default_factory=ProcessManager)
    metrics: SimulationMetrics = field(default_factory=SimulationMetrics)
    scheduler: Scheduler | None = None
    _monitor_thread: threading.Thread | None = None
    _atm_threads: list[threading.Thread] = field(default_factory=list)
    _running: bool = False
    _current_tick: int = 0
    _status_log: list[str] = field(default_factory=list)
    _status_lock: threading.Lock = field(default_factory=threading.Lock)

    def _log_status(self, msg: str) -> None:
        with self._status_lock:
            self._status_log.append(msg)

    def get_status_log(self) -> list[str]:
        with self._status_lock:
            return list(self._status_log)

    def setup(self) -> None:
        self.process_manager = ProcessManager()
        self.metrics = SimulationMetrics()
        BankingOperationFactory.generate_banking_workload(
            self.process_manager,
            self.config.num_processes,
            quantum=self.config.quantum,
        )
        if self.config.scheduler_type == "PRIORITY":
            self.scheduler = PriorityScheduler(self.process_manager, self.metrics)
        else:
            self.scheduler = RoundRobinScheduler(
                self.process_manager,
                self.metrics,
                quantum=self.config.quantum,
            )

    def _maybe_block_current(self) -> None:
        if (
            self.scheduler
            and self.scheduler.current_process
            and random.random() < self.config.block_probability
        ):
            pid = self.scheduler.current_process.pid
            self.process_manager.block_process(pid)
            self._log_status(f"Tick {self._current_tick}: PID {pid} bloqueado (aguardando conta)")
            self.scheduler.current_process = None

    def run(
        self,
        step_by_step: bool = False,
        on_tick: Callable[[int, ProcessManager, SimulationMetrics], None] | None = None,
    ) -> SimulationMetrics:
        if not self.scheduler:
            self.setup()

        assert self.scheduler is not None
        self._running = True
        self._current_tick = 0
        max_ticks = 500

        def sleep_fn() -> None:
            if not self.config.fast_mode and self.config.tick_delay > 0:
                time.sleep(self.config.tick_delay)

        while self._running and self._current_tick < max_ticks:
            active = self.process_manager.get_active_processes()
            running_or_ready = [
                p for p in active if p.state not in (ProcessState.TERMINATED, ProcessState.NEW)
            ]
            if not running_or_ready and not self.process_manager.ready_queue:
                pending = [
                    p for p in active if p.state == ProcessState.NEW
                ]
                if not pending:
                    break

            if random.random() < 0.1:
                for pid in list(self.process_manager.blocked_queue):
                    self.process_manager.unblock_process(pid)
                    self._log_status(f"Tick {self._current_tick}: PID {pid} desbloqueado")

            continues = self.scheduler.tick(self._current_tick, sleep_fn=sleep_fn)
            self._maybe_block_current()
            self.metrics.total_ticks = self._current_tick + 1

            ready_pcbs = [
                self.process_manager.get_process(pid)
                for pid in self.process_manager.ready_queue
            ]
            self.metrics.record_queue_snapshot(ready_pcbs, self._current_tick)

            if on_tick:
                on_tick(self._current_tick, self.process_manager, self.metrics)

            if step_by_step:
                input("  [Enter] proximo tick...")

            self._current_tick += 1
            if not continues and not self.process_manager.ready_queue:
                pending = [
                    p
                    for p in self.process_manager.get_active_processes()
                    if p.state in (ProcessState.NEW, ProcessState.BLOCKED)
                ]
                if not pending:
                    break

        self._running = False
        return self.metrics

    def start_monitor_thread(self, interval: float = 0.5) -> None:
        def monitor() -> None:
            while self._running:
                ready = len(self.process_manager.ready_queue)
                blocked = len(self.process_manager.blocked_queue)
                done = len(self.process_manager.terminated)
                self._log_status(
                    f"[Monitor] tick={self._current_tick} "
                    f"ready={ready} blocked={blocked} done={done}"
                )
                time.sleep(interval)

        self._monitor_thread = threading.Thread(target=monitor, name="AuditMonitor", daemon=True)
        self._monitor_thread.start()

    def run_concurrent_atm_demo(self) -> dict:
        """Threads ATM produzindo transacoes em paralelo com monitor."""
        from pathlib import Path

        from src.banking.transactions import TransactionType
        from src.concurrency.sync_primitives import BankSemaphore

        buffer = ProducerConsumerBuffer(capacity=5)
        tx_log = TransactionLog(Path("logs/transactions.log"))
        atm_semaphore = BankSemaphore(self.config.num_atm_threads, "atm_slots")

        self._running = True
        results: dict = {"produced": 0, "log_entries": []}

        def atm_worker(atm_id: int) -> None:
            for i in range(3):
                if atm_semaphore.acquire(timeout=2):
                    try:
                        tx_type = random.choice(list(TransactionType))
                        buffer.produce(atm_id, tx_type, 50.0 + i * 10)
                        tx_log.append_safe(f"ATM-{atm_id} registrou {tx_type.value}")
                        results["produced"] += 1
                        time.sleep(0.05)
                    finally:
                        atm_semaphore.release()

        def backend_worker() -> None:
            for _ in range(self.config.num_atm_threads * 3):
                tx = buffer.consume(1)
                if tx:
                    tx_log.append_safe(f"Backend processou TX-{tx.tx_id}")
                time.sleep(0.08)

        self.start_monitor_thread(interval=0.3)
        atm_threads = [
            threading.Thread(target=atm_worker, args=(i + 1,), name=f"ATM-{i+1}")
            for i in range(self.config.num_atm_threads)
        ]
        backend = threading.Thread(target=backend_worker, name="Backend")
        for t in atm_threads:
            t.start()
        backend.start()
        for t in atm_threads:
            t.join()
        backend.join()
        self._running = False

        results["buffer_stats"] = buffer.stats()
        results["monitor_log"] = self.get_status_log()[-10:]
        return results
