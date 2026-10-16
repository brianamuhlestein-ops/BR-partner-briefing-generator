from __future__ import annotations

from dataclasses import dataclass, field
from threading import Event, Lock
from typing import Callable, Generic, Hashable, TypeVar, cast


T = TypeVar("T")


@dataclass
class _InFlight(Generic[T]):
    ready: Event = field(default_factory=Event)
    result: T | None = None
    error: BaseException | None = None


class SingleFlight:
    """Share identical work only while that work is actively in progress."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._calls: dict[Hashable, _InFlight[object]] = {}

    def run(self, key: Hashable, operation: Callable[[], T]) -> T:
        with self._lock:
            call = self._calls.get(key)
            if call is None:
                call = _InFlight()
                self._calls[key] = call
                leader = True
            else:
                leader = False

        if leader:
            try:
                call.result = operation()
            except BaseException as exc:
                call.error = exc
            finally:
                call.ready.set()
                with self._lock:
                    if self._calls.get(key) is call:
                        del self._calls[key]
        else:
            call.ready.wait()

        if call.error is not None:
            raise call.error
        return cast(T, call.result)
