from dataclasses import dataclass, field

from src.core.process import PCB, ProcessState


@dataclass
class SimulationMetrics:
    completed: list[PCB] = field(default_factory=list)
    queue_snapshots: list[list[dict]] = field(default_factory=list)
    total_ticks: int = 0
    deadline_misses: int = 0
    memory_stats: dict = field(default_factory=dict)

    def record_completion(self, pcb: PCB) -> None:
        self.completed.append(pcb)
        if pcb.finish_time is not None and pcb.finish_time > pcb.deadline:
            pcb.deadline_missed = True
            self.deadline_misses += 1

    def record_queue_snapshot(self, queue: list[PCB], tick: int) -> None:
        snapshot = [
            {"pid": p.pid, "name": p.name, "state": p.state.value, "tick": tick}
            for p in queue
        ]
        self.queue_snapshots.append(snapshot)

    @property
    def avg_waiting_time(self) -> float:
        if not self.completed:
            return 0.0
        return sum(p.waiting_time for p in self.completed) / len(self.completed)

    @property
    def avg_response_time(self) -> float:
        times = [p.response_time for p in self.completed if p.response_time is not None]
        if not times:
            return 0.0
        return sum(times) / len(times)

    @property
    def avg_turnaround_time(self) -> float:
        times = [
            p.turnaround_time for p in self.completed if p.turnaround_time is not None
        ]
        if not times:
            return 0.0
        return sum(times) / len(times)

    def summary(self) -> dict:
        return {
            "total_ticks": self.total_ticks,
            "completed_count": len(self.completed),
            "avg_waiting_time": round(self.avg_waiting_time, 2),
            "avg_response_time": round(self.avg_response_time, 2),
            "avg_turnaround_time": round(self.avg_turnaround_time, 2),
            "deadline_misses": self.deadline_misses,
            "memory": self.memory_stats,
        }

    def completed_report(self) -> list[dict]:
        return [
            {
                "pid": p.pid,
                "operation": p.operation_type,
                "priority": p.priority.name,
                "waiting_time": p.waiting_time,
                "response_time": p.response_time,
                "turnaround_time": p.turnaround_time,
                "finish_time": p.finish_time,
                "deadline": p.deadline,
                "deadline_missed": p.deadline_missed,
            }
            for p in self.completed
        ]
