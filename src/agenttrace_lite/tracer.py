
import token
from unicodedata import name
import uuid
import functools
from contextvars import ContextVar
import inspect
import threading
from contextlib import contextmanager
from .span import Span
from .exporter import JSONLExporter


class Tracer:

    def __init__(
        self,
        service_name="agenttrace-app",
        output="agenttrace_traces.jsonl"
    ):
        self.service_name = service_name
        self.spans = []
        self.exporter = JSONLExporter(output)
        self._lock = threading.Lock()

        self._current_span = ContextVar(
            f"agenttrace_current_span_{id(self)}",
            default=None
        )

    def trace(self, func):

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):

                parent = self._current_span.get()

                trace_id = (
                    parent.trace_id
                    if parent
                    else str(uuid.uuid4())
                )

                span = Span(
                    name=func.__name__,
                    trace_id=trace_id,
                    parent_span_id=(
                        parent.span_id if parent else None
                    ),
                   service_name=self.service_name,
                )

                with self._lock:
                    self.spans.append(span)

                token = self._current_span.set(span)

                try:
                    result = await func(*args, **kwargs)
                    span.finish()
                    return result

                except Exception as e:
                    span.fail(e)
                    raise

                finally:
                    self._current_span.reset(token)

            return async_wrapper

        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):

                parent = self._current_span.get()

                trace_id = (
                    parent.trace_id
                    if parent
                    else str(uuid.uuid4())
                )

                span = Span(
                    name=func.__name__,
                    trace_id=trace_id,
                    parent_span_id=(
                        parent.span_id if parent else None
                    ),
                    service_name=self.service_name
                )

                with self._lock:
                     self.spans.append(span)

                token = self._current_span.set(span)

                try:
                    result = func(*args, **kwargs)
                    span.finish()
                    return result

                except Exception as e:
                    span.fail(e)
                    raise

                finally:
                    self._current_span.reset(token)

            return sync_wrapper

    @contextmanager
    def span(self, name):
        parent = self._current_span.get()

        trace_id = (
            parent.trace_id
            if parent
            else str(uuid.uuid4())
        )

        span = Span(
            name=name,
            trace_id=trace_id,
            parent_span_id=parent.span_id if parent else None,
            service_name=self.service_name
        )

        with self._lock:
            self.spans.append(span)

        token = self._current_span.set(span)

        try:
            yield span
            span.finish()

        except Exception as e:
            span.fail(e)
            raise

        finally:
            self._current_span.reset(token)
    def get_spans(
        self,
        name=None,
        status=None,
        trace_id=None
    ):
        """Return spans matching the provided filters."""

        with self._lock:
            spans = self.spans.copy()

        if name is not None:
            spans = [
                span for span in spans
                if span.name == name
            ]

        if status is not None:
            spans = [
                span for span in spans
                if span.status == status
            ]

        if trace_id is not None:
            spans = [
                span for span in spans
                if span.trace_id == trace_id
            ]

        return spans

    def flush(self):
        """Export collected spans safely."""
        with self._lock:
             spans_to_export = self.spans.copy()
             self.spans.clear()

        self.exporter.export(spans_to_export)
