import threading
from dataclasses import dataclass, field

from src.concurrency.sync_primitives import BankMutex


@dataclass
class MemoryFrame:
    frame_id: int
    pid: int | None = None
    page_id: int | None = None
    label: str = "livre"


@dataclass
class BankMemoryManager:
    """Gerenciador de memoria: aloca quadros (frames) para cache de dados bancarios."""

    total_frames: int = 16
    page_size_kb: int = 4
    frames: list[MemoryFrame] = field(init=False)
    allocated_pages: dict[int, int] = field(default_factory=dict)
    page_faults: int = 0
    allocations: int = 0
    deallocations: int = 0
    _mutex: BankMutex = field(default_factory=lambda: BankMutex("memoria"))

    def __post_init__(self) -> None:
        self.frames = [
            MemoryFrame(frame_id=i, label="livre") for i in range(self.total_frames)
        ]

    @property
    def free_frames(self) -> int:
        return sum(1 for f in self.frames if f.pid is None)

    @property
    def used_frames(self) -> int:
        return self.total_frames - self.free_frames

    def allocate(self, pid: int, pages: int) -> bool:
        with self._mutex:
            free = [f for f in self.frames if f.pid is None]
            if len(free) < pages:
                self.page_faults += 1
                return False

            for i in range(pages):
                frame = free[i]
                frame.pid = pid
                frame.page_id = i
                frame.label = f"cache-conta-p{pid}"

            self.allocated_pages[pid] = pages
            self.allocations += 1
            return True

    def free(self, pid: int) -> int:
        with self._mutex:
            freed = 0
            for frame in self.frames:
                if frame.pid == pid:
                    frame.pid = None
                    frame.page_id = None
                    frame.label = "livre"
                    freed += 1
            if pid in self.allocated_pages:
                del self.allocated_pages[pid]
            if freed:
                self.deallocations += 1
            return freed

    def get_map(self) -> list[dict]:
        return [
            {
                "frame": f.frame_id,
                "pid": f.pid,
                "page": f.page_id,
                "label": f.label,
            }
            for f in self.frames
        ]

    def summary(self) -> dict:
        return {
            "total_frames": self.total_frames,
            "used_frames": self.used_frames,
            "free_frames": self.free_frames,
            "page_size_kb": self.page_size_kb,
            "page_faults": self.page_faults,
            "allocations": self.allocations,
            "deallocations": self.deallocations,
        }
