from collections import Counter
from threading import Lock


class MetricsService:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Counter[str] = Counter()

    def increment(self, metric_name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[metric_name] += amount

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)
