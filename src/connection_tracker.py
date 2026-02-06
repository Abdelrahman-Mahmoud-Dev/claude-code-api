"""Active connections tracker for live monitoring of API usage."""

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ActiveConnection:
    """Represents a currently active API request."""

    request_id: str
    client_ip: str
    endpoint: str
    method: str
    model: Optional[str]
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        now = datetime.now(timezone.utc)
        duration = (now - self.start_time).total_seconds()
        return {
            "request_id": self.request_id,
            "client_ip": self.client_ip,
            "endpoint": self.endpoint,
            "method": self.method,
            "model": self.model,
            "started_at": self.start_time.isoformat(),
            "duration_seconds": round(duration, 2),
        }


@dataclass
class CompletedConnection:
    """Represents a recently completed API request."""

    request_id: str
    client_ip: str
    endpoint: str
    method: str
    model: Optional[str]
    started_at: datetime
    completed_at: datetime
    status_code: int
    duration_seconds: float

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "client_ip": self.client_ip,
            "endpoint": self.endpoint,
            "method": self.method,
            "model": self.model,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "status_code": self.status_code,
            "duration_seconds": round(self.duration_seconds, 2),
        }


class ConnectionTracker:
    """Tracks active and recently completed API connections with SSE broadcasting."""

    def __init__(self, max_recent: int = 50):
        self._active: Dict[str, ActiveConnection] = {}
        self._recent: deque = deque(maxlen=max_recent)
        self._lock = Lock()
        self._subscribers: List[asyncio.Queue] = []
        self._total_today: int = 0
        self._today_date: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def start_request(
        self,
        request_id: str,
        client_ip: str,
        endpoint: str,
        method: str,
        model: Optional[str] = None,
    ) -> None:
        """Record a new active request."""
        conn = ActiveConnection(
            request_id=request_id,
            client_ip=client_ip,
            endpoint=endpoint,
            method=method,
            model=model,
        )
        with self._lock:
            self._active[request_id] = conn
            # Reset daily counter if new day
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if today != self._today_date:
                self._today_date = today
                self._total_today = 0
            self._total_today += 1

        self._schedule_broadcast(
            {
                "event": "request_started",
                "data": conn.to_dict(),
                "active_count": len(self._active),
            }
        )
        logger.debug(f"Connection started: {request_id} from {client_ip} -> {endpoint}")

    def end_request(self, request_id: str, status_code: int = 200) -> None:
        """Record that a request has completed."""
        with self._lock:
            conn = self._active.pop(request_id, None)
            if not conn:
                return

            now = datetime.now(timezone.utc)
            duration = (now - conn.start_time).total_seconds()

            completed = CompletedConnection(
                request_id=conn.request_id,
                client_ip=conn.client_ip,
                endpoint=conn.endpoint,
                method=conn.method,
                model=conn.model,
                started_at=conn.start_time,
                completed_at=now,
                status_code=status_code,
                duration_seconds=duration,
            )
            self._recent.appendleft(completed)

        self._schedule_broadcast(
            {
                "event": "request_completed",
                "data": completed.to_dict(),
                "active_count": len(self._active),
            }
        )
        logger.debug(f"Connection ended: {request_id} ({duration:.2f}s, status={status_code})")

    def get_active(self) -> List[dict]:
        """Get all currently active connections."""
        with self._lock:
            return [conn.to_dict() for conn in self._active.values()]

    def get_recent(self) -> List[dict]:
        """Get recently completed connections."""
        with self._lock:
            return [conn.to_dict() for conn in self._recent]

    def get_stats(self) -> dict:
        """Get connection statistics."""
        with self._lock:
            active_count = len(self._active)
            recent_list = list(self._recent)
            total_today = self._total_today

        avg_duration = 0.0
        if recent_list:
            avg_duration = sum(c.duration_seconds for c in recent_list) / len(recent_list)

        return {
            "active_count": active_count,
            "total_today": total_today,
            "recent_completed": len(recent_list),
            "avg_duration_seconds": round(avg_duration, 2),
        }

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to live connection updates (SSE)."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        logger.debug(f"SSE subscriber added (total: {len(self._subscribers)})")
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Unsubscribe from live connection updates."""
        try:
            self._subscribers.remove(queue)
            logger.debug(f"SSE subscriber removed (total: {len(self._subscribers)})")
        except ValueError:
            pass

    def _schedule_broadcast(self, event: dict) -> None:
        """Schedule an SSE broadcast to all subscribers."""
        message = json.dumps(event)
        stale = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                stale.append(queue)
        # Clean up stale subscribers
        for q in stale:
            self.unsubscribe(q)


# Global singleton
connection_tracker = ConnectionTracker()
