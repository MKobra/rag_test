from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, status


_events: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def enforce_limit(key: str, limit: int, window_seconds: int) -> None:
    now = monotonic()
    with _lock:
        events = _events[key]
        while events and events[0] <= now - window_seconds:
            events.popleft()
        if len(events) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Лимит запросов временно исчерпан",
                headers={"Retry-After": str(window_seconds)},
            )
        events.append(now)
