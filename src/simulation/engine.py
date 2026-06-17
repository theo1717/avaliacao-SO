import random
import threading
import time
from dataclasses import dataclass, field
from typing import Callable

from src.banking.account_locks import AccountLockManager
from src.banking.operations import BankingOperationFactory
from src.concurrency.producer_consumer import ProducerConsumerBuffer
from src.concurrency.sync_primitives import BankSemaphore, TransactionLog
from src.core.memory import BankMemoryManager
from src.core.metrics import SimulationMetrics
from src.core.process import PCB, ProcessState
from src.core.process_manager import ProcessManager
from src.core.scheduler import (
    EDFScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
    Scheduler,
)


@dataclass
class SimulationConfig:
    quantum: int = 2
    num_processes: int = 8
    tick_delay: float = 0.1
    fast_mode: bool = False
    num_atm_threads: int = 2
    scheduler_type: str = "RR"
    memory_frames: int = 16


@dataclass
class SimulationEngine:
    config: SimulationConfig = field(default_factory=SimulationConfig)
    process_manager: ProcessManager = field(default_factory=ProcessManager)
    metrics: SimulationMetrics = field(default_factory=SimulationMetrics)
    memory: BankMemoryManager = field(default_factory=BankMemoryManager)
    account_locks: AccountLockManager = field(default_factory=AccountLockManager)
    scheduler: Scheduler | None = None
    _monitor_thread: threading.Thread | None = None
    _running: bool = False
    _current_tick: int = 0
    _last_terminated_count: int = 0
    _status_log: list[str] = field(default_factory=list)
    _status_lock: threading.Lock = field(default_factory=threading.Lock)

    def _log_status(self, msg: str) -> None:
        with self._status_lock:
            self._status_log.append(msg)

    def get_status_log(self) -> list[str]:
        with self._status_lock:
            return list(self._status_log)

    def _resource_gate(self, pcb: PCB, current_tick: int) -> bool:
        if pcb.needs_account_lock():
            if not self.account_locks.try_acquire(pcb.account_id, pcb.pid):
                pcb.block_reason = f"conta_{pcb.account_id}"
                self.process_manager.block_process(pcb.pid)
                self._log_status(
                    f"Tick {current_tick}: PID {pcb.pid} bloqueado "
                    f"(conta {pcb.account_id} em uso)"
                )
                return False
        return True

    def _try_allocate_memory(self, pid: int) -> bool:
        pcb = self.process_manager.get_process(pid)
        if pid in self.memory.allocated_pages:
            return True
        if self.memory.allocate(pid, pcb.pages_required):
            return True
        pcb.block_reason = "memoria"
        if pcb.state == ProcessState.READY:
            self.process_manager.block_process(pid)
        self._log_status(
            f"PID {pid} bloqueado (aguardando {pcb.pages_required} pagina(s) de memoria)"
        )
        return False

    def _release_process_resources(self, pid: int) -> None:
        self.memory.free(pid)
        released_accounts = self.account_locks.release_all_for_process(pid)
        if released_accounts:
            self._log_status(f"PID {pid} liberou contas {released_accounts}")

    def _try_unblock_waiters(self) -> None:
        for pid in list(self.process_manager.blocked_queue):
            pcb = self.process_manager.get_process(pid)
            if pcb.block_reason == "memoria":
                if self.memory.allocate(pid, pcb.pages_required):
                    pcb.block_reason = ""
                    self.process_manager.unblock_process(pid)
                    self._log_status(f"PID {pid} desbloqueado (memoria alocada)")
            elif pcb.block_reason.startswith("conta_"):
                if self.account_locks.try_acquire(pcb.account_id, pid):
                    pcb.block_reason = ""
                    self.process_manager.unblock_process(pid)
                    self._log_status(
                        f"PID {pid} desbloqueado (conta {pcb.account_id} disponivel)"
                    )

    def _handle_newly_terminated(self) -> None:
        terminated = self.process_manager.terminated[self._last_terminated_count :]
        for pid in terminated:
            self._release_process_resources(pid)
        self._last_terminated_count = len(self.process_manager.terminated)
        if terminated:
            self._try_unblock_waiters()

    def _admit_and_allocate(self, current_tick: int) -> None:
        admitted = self.process_manager.admit_arrived(current_tick)
        for pid in admitted:
            self._try_allocate_memory(pid)

    def setup(self) -> None:
        self.process_manager = ProcessManager()
        self.metrics = SimulationMetrics()
        self.memory = BankMemoryManager(total_frames=self.config.memory_frames)
        self.account_locks = AccountLockManager()
        self._last_terminated_count = 0

        BankingOperationFactory.generate_banking_workload(
            self.process_manager,
            self.config.num_processes,
            quantum=self.config.quantum,
        )

        gate = self._resource_gate
        if self.config.scheduler_type == "PRIORITY":
            self.scheduler = PriorityScheduler(
                self.process_manager, self.metrics, resource_gate=gate
            )
        elif self.config.scheduler_type == "EDF":
            self.scheduler = EDFScheduler(
                self.process_manager, self.metrics, resource_gate=gate
            )
        else:
            self.scheduler = RoundRobinScheduler(
                self.process_manager,
                self.metrics,
                quantum=self.config.quantum,
                resource_gate=gate,
            )

        for pid in list(self.process_manager.ready_queue):
            self._try_allocate_memory(pid)

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
            self._admit_and_allocate(self._current_tick)
            self._try_unblock_waiters()

            active = self.process_manager.get_active_processes()
            running_or_ready = [
                p for p in active if p.state not in (ProcessState.TERMINATED, ProcessState.NEW)
            ]
            if not running_or_ready and not self.process_manager.ready_queue:
                pending = [p for p in active if p.state == ProcessState.NEW]
                if not pending and not self.process_manager.blocked_queue:
                    break

            continues = self.scheduler.tick(self._current_tick, sleep_fn=sleep_fn)
            self._handle_newly_terminated()

            if (
                self.scheduler.current_process
                and self._current_tick > self.scheduler.current_process.deadline
                and self.scheduler.current_process.state == ProcessState.RUNNING
            ):
                pcb = self.scheduler.current_process
                pcb.deadline_missed = True

            self.metrics.total_ticks = self._current_tick + 1
            self.metrics.memory_stats = self.memory.summary()

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
        self.metrics.memory_stats = self.memory.summary()
        return self.metrics

    def start_monitor_thread(self, interval: float = 0.5) -> None:
        def monitor() -> None:
            while self._running:
                ready = len(self.process_manager.ready_queue)
                blocked = len(self.process_manager.blocked_queue)
                done = len(self.process_manager.terminated)
                mem = self.memory.summary()
                self._log_status(
                    f"[Monitor] tick={self._current_tick} "
                    f"ready={ready} blocked={blocked} done={done} "
                    f"mem={mem['used_frames']}/{mem['total_frames']}"
                )
                time.sleep(interval)

        self._monitor_thread = threading.Thread(
            target=monitor, name="AuditMonitor", daemon=True
        )
        self._monitor_thread.start()

    def run_concurrent_atm_demo(self) -> dict:
        from pathlib import Path

        from src.banking.transactions import TransactionType

        buffer = ProducerConsumerBuffer(capacity=5)
        tx_log = TransactionLog(Path("logs/transactions.log"))
        atm_semaphore = BankSemaphore(self.config.num_atm_threads, "atm_slots")

        self._running = True
        results: dict = {"produced": 0}

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

    def run_memory_pressure_demo(self) -> dict:
        """Demonstra alocacao/liberacao de memoria com poucos quadros."""
        from src.core.process import Priority

        self.process_manager = ProcessManager()
        self.memory = BankMemoryManager(total_frames=6)
        self._status_log.clear()
        log: list[str] = []

        processes: list[PCB] = []
        for i in range(5):
            burst = random.randint(3, 6)
            pcb = self.process_manager.create_process(
                name=f"MemProc-{i+1}",
                priority=random.choice(list(Priority)),
                burst_time=burst,
                arrival_time=0,
                pages_required=2,
                operation_type="Extrato",
            )
            processes.append(pcb)

        allocated_count = 0
        blocked: list[int] = []
        for pcb in processes:
            if self.memory.allocate(pcb.pid, pcb.pages_required):
                allocated_count += 1
                log.append(f"PID {pcb.pid}: alocado {pcb.pages_required} pagina(s)")
            else:
                blocked.append(pcb.pid)
                pcb.block_reason = "memoria"
                log.append(f"PID {pcb.pid}: BLOQUEADO (sem quadros livres)")

        freed_pid = processes[0].pid
        freed = self.memory.free(freed_pid)
        log.append(f"PID {freed_pid}: liberou {freed} quadro(s)")

        unblocked = 0
        for pid in blocked:
            pcb = self.process_manager.get_process(pid)
            if self.memory.allocate(pid, pcb.pages_required):
                unblocked += 1
                log.append(f"PID {pid}: desbloqueado apos liberacao de memoria")

        return {
            "memory": self.memory.summary(),
            "memory_map": self.memory.get_map(),
            "allocated_initial": allocated_count,
            "blocked_initial": len(blocked),
            "unblocked_after_free": unblocked,
            "log": log,
        }
