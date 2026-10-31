
from agenttrace_lite import Span


def test_span_creation():
    span = Span(name="test_span", trace_id="trace-123")

    assert span.name == "test_span"
    assert span.trace_id == "trace-123"
    assert span.status == "running"
    assert span.end_time is None


def test_span_finish():
    span = Span(name="test_span", trace_id="trace-123")

    span.finish()

    assert span.status == "ok"
    assert span.end_time is not None
    assert span.duration_ms is not None


def test_span_attributes():
    span = Span(name="test_span", trace_id="trace-123")

    span.set_attribute("model", "gpt-4")
    span.set_attribute("tokens", 100)

    assert span.attributes["model"] == "gpt-4"
    assert span.attributes["tokens"] == 100


def test_span_failure():
    span = Span(name="test_span", trace_id="trace-123")

    error = ValueError("Something went wrong")
    span.fail(error)

    assert span.status == "error"
    assert span.error == "Something went wrong"
    assert span.end_time is not None
