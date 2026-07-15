from collections import defaultdict
import threading
from typing import Any


class ExecutionObserver:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.events: list[dict[str, Any]] = []
        self.metrics: dict[str, int] = defaultdict(int)
        self.scan_history: dict[int, list[dict[str, Any]]] = {}

    def record(self, event: str, details: dict[str, Any] | None = None) -> None:
        with self._lock:
            payload = {"event": event, "details": details or {}}
            self.events.append(payload)
            self.metrics[event] += 1
            scan_id = details.get("scan_id") if details else None
            if isinstance(scan_id, int):
                self.scan_history.setdefault(scan_id, []).append(payload)

    def snapshot(self, event: str | None = None) -> dict[str, Any]:
        with self._lock:
            events = list(self.events)
            if event is not None:
                events = [entry for entry in events if entry.get("event") == event]
                metrics = {event: self.metrics.get(event, 0)} if event in self.metrics else {}
            else:
                metrics = dict(self.metrics)
            return {"events": events, "metrics": metrics}

    def history_for_scan(self, scan_id: int) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.scan_history.get(scan_id, []))

    def events_for_scan(self, scan_id: int) -> list[dict[str, Any]]:
        with self._lock:
            return [event for event in self.events if event.get("details", {}).get("scan_id") == scan_id]


class AuditTrail:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def record(self, *, actor: str, action: str, resource_type: str, resource_id: int | None = None, details: dict[str, Any] | None = None) -> None:
        self.entries.append({
            "actor": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
        })

    def list(self, *, actor: str | None = None, action: str | None = None) -> list[dict[str, Any]]:
        entries = list(self.entries)
        if actor is not None:
            entries = [entry for entry in entries if entry.get("actor") == actor]
        if action is not None:
            entries = [entry for entry in entries if entry.get("action") == action]
        return entries


observer = ExecutionObserver()
audit_trail = AuditTrail()
