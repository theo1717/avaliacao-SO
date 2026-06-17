from abc import ABC, abstractmethod
from collections import deque

from src.core.metrics import SimulationMetrics
from src.core.process import PCB, ProcessState
from src.core.process_manager import ProcessManager


class Scheduler(ABC):
    def __init__(
        self,
        process_manager: ProcessManager,
        metrics: SimulationMetrics,
        resource_gate=None,
    ) -> None:
        self.pm = process_manager
        self.metrics = metrics
        self.resource_gate = resource_gate
        self.current_process: PCB | None = None
        self.quantum_remaining: int = 0

    def _acquire_next_ready(self, current_tick: int) -> PCB | None:
        attempts = len(self.pm.ready_queue) + 1
        for _ in range(max(attempts, 1)):
            next_pcb = self.select_next()
            if next_pcb is None:
                return None
            if self.resource_gate and not self.resource_gate(next_pcb, current_tick):
                continue
            return next_pcb
        return None

    @abstractmethod
    def select_next(self) -> PCB | None:
        pass

    @abstractmethod
    def on_preempt(self, pcb: PCB) -> None:
        pass

    def tick(self, current_tick: int, sleep_fn=None) -> bool:
        """Execute one simulation tick. Returns True if simulation continues."""
        for pid in list(self.pm.ready_queue):
            pcb = self.pm.get_process(pid)
            if pcb.state == ProcessState.READY and pcb.last_scheduled_tick != current_tick:
                pcb.waiting_time += 1

        if self.current_process is None or self.current_process.state != ProcessState.RUNNING:
            next_pcb = self._acquire_next_ready(current_tick)
            if next_pcb is None:
                active = self.pm.get_active_processes()
                if not active or all(
                    p.state in (ProcessState.TERMINATED, ProcessState.BLOCKED, ProcessState.NEW)
                    for p in active
                ):
                    return False
                return True

            self.current_process = next_pcb
            self.current_process.state = ProcessState.RUNNING
            if self.current_process.start_time is None:
                self.current_process.start_time = current_tick
            self.quantum_remaining = self.current_process.quantum

        pcb = self.current_process
        pcb.remaining_time -= 1
        self.quantum_remaining -= 1
        pcb.last_scheduled_tick = current_tick

        if sleep_fn:
            sleep_fn()

        if pcb.remaining_time <= 0:
            pcb.state = ProcessState.TERMINATED
            pcb.finish_time = current_tick + 1
            self.pm.terminate_process(pcb.pid)
            self.metrics.record_completion(pcb)
            self.current_process = None
            return True

        if self.quantum_remaining <= 0:
            self.on_preempt(pcb)
            self.current_process = None

        return True


class RoundRobinScheduler(Scheduler):
    def __init__(
        self,
        process_manager: ProcessManager,
        metrics: SimulationMetrics,
        quantum: int = 2,
        resource_gate=None,
    ) -> None:
        super().__init__(process_manager, metrics, resource_gate=resource_gate)
        self.quantum = quantum
        self._queue: deque[int] = deque()

    def _rebuild_queue(self) -> None:
        self._queue = deque(self.pm.ready_queue)

    def select_next(self) -> PCB | None:
        if not self._queue:
            self._rebuild_queue()
        while self._queue:
            pid = self._queue.popleft()
            pcb = self.pm.get_process(pid)
            if pcb.state == ProcessState.READY:
                self.quantum_remaining = self.quantum
                return pcb
        return None

    def on_preempt(self, pcb: PCB) -> None:
        pcb.state = ProcessState.READY
        if pcb.pid not in self.pm.ready_queue:
            self.pm.ready_queue.append(pcb.pid)
        self._queue.append(pcb.pid)


class PriorityScheduler(Scheduler):
    def __init__(
        self,
        process_manager: ProcessManager,
        metrics: SimulationMetrics,
        aging_interval: int = 5,
        resource_gate=None,
    ) -> None:
        super().__init__(process_manager, metrics, resource_gate=resource_gate)
        self.aging_interval = aging_interval
        self._ticks_since_aging = 0

    def _apply_aging(self, current_tick: int) -> None:
        self._ticks_since_aging += 1
        if self._ticks_since_aging < self.aging_interval:
            return
        self._ticks_since_aging = 0
        for pid in self.pm.ready_queue:
            pcb = self.pm.get_process(pid)
            if pcb.priority.value < 2:
                from src.core.process import Priority

                pcb.priority = Priority(pcb.priority.value + 1)

    def select_next(self) -> PCB | None:
        ready = [
            self.pm.get_process(pid)
            for pid in self.pm.ready_queue
            if self.pm.get_process(pid).state == ProcessState.READY
        ]
        if not ready:
            return None
        ready.sort(key=lambda p: (p.priority.value, p.arrival_time, p.pid))
        selected = ready[0]
        self.quantum_remaining = selected.remaining_time
        return selected

    def on_preempt(self, pcb: PCB) -> None:
        pcb.state = ProcessState.READY

    def tick(self, current_tick: int, sleep_fn=None) -> bool:
        self._apply_aging(current_tick)
        return super().tick(current_tick, sleep_fn)


class EDFScheduler(Scheduler):
    """Earliest Deadline First - escalonamento em tempo real por deadline."""

    def select_next(self) -> PCB | None:
        ready = [
            self.pm.get_process(pid)
            for pid in self.pm.ready_queue
            if self.pm.get_process(pid).state == ProcessState.READY
        ]
        if not ready:
            return None
        ready.sort(key=lambda p: (p.deadline, p.arrival_time, p.pid))
        selected = ready[0]
        self.quantum_remaining = selected.remaining_time
        return selected

    def on_preempt(self, pcb: PCB) -> None:
        pcb.state = ProcessState.READY

    def tick(self, current_tick: int, sleep_fn=None) -> bool:
        if (
            self.current_process
            and self.current_process.state == ProcessState.RUNNING
        ):
            ready = [
                self.pm.get_process(pid)
                for pid in self.pm.ready_queue
                if self.pm.get_process(pid).state == ProcessState.READY
            ]
            if ready:
                earliest = min(ready, key=lambda p: (p.deadline, p.pid))
                if earliest.deadline < self.current_process.deadline:
                    self.on_preempt(self.current_process)
                    self.current_process = None

        return super().tick(current_tick, sleep_fn)
