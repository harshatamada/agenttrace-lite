
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class Span:
    name: str
    trace_id: str
    parent_span_id: Optional[str] = None
    service_name: str = "agenttrace-app"

    span_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    start_time: float = field(
        default_factory=time.time
    )

    end_time: Optional[float] = None
    status: str = "running"

    attributes: dict[str, Any] = field(
        default_factory=dict
    )

    error: Optional[str] = None

    def set_attribute(self, key: str, value: Any):
        """Attach metadata to this span."""
        self.attributes[key] = value

    def finish(self):
        """Mark the span as completed."""
        if self.end_time is None:
            self.end_time = time.time()

            if self.status == "running":
                self.status = "ok"

    def fail(self, exception: Exception):
        """Mark the span as failed."""
        self.end_time = time.time()
        self.status = "error"
        self.error = str(exception)

    @property
    def duration_ms(self) -> Optional[float]:
        """Return execution duration in milliseconds."""
        if self.end_time is None:
            return None

        return round(
            (self.end_time - self.start_time) * 1000,
            2
        )

    def to_dict(self) -> dict:
        """Convert span into a serializable dictionary."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
            "error": self.error,
            "service_name": self.service_name,
        }
