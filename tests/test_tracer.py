
import json
from agenttrace_lite import Tracer


def test_tracer_creates_span(tmp_path):
    output = tmp_path / "traces.jsonl"

    tracer = Tracer(output=str(output))

    @tracer.trace
    def hello():
        return "hello"

    result = hello()

    assert result == "hello"
    assert len(tracer.spans) == 1
    assert tracer.spans[0].name == "hello"
    assert tracer.spans[0].status == "ok"


def test_nested_spans(tmp_path):
    output = tmp_path / "traces.jsonl"

    tracer = Tracer(output=str(output))

    @tracer.trace
    def child():
        return "child result"

    @tracer.trace
    def parent():
        return child()

    parent()

    assert len(tracer.spans) == 2

    parent_span = next(
        span for span in tracer.spans
        if span.name == "parent"
    )

    child_span = next(
        span for span in tracer.spans
        if span.name == "child"
    )

    assert child_span.trace_id == parent_span.trace_id
    assert child_span.parent_span_id == parent_span.span_id


def test_tracer_exports_jsonl(tmp_path):
    output = tmp_path / "traces.jsonl"

    tracer = Tracer(output=str(output))

    @tracer.trace
    def task():
        return "done"

    task()
    tracer.flush()

    assert output.exists()

    with output.open() as file:
        record = json.loads(file.readline())

    assert record["name"] == "task"
    assert record["status"] == "ok"
    assert "trace_id" in record
    assert "span_id" in record


def test_tracer_records_errors(tmp_path):
    output = tmp_path / "traces.jsonl"

    tracer = Tracer(output=str(output))

    @tracer.trace
    def failing_task():
        raise ValueError("Test failure")

    try:
        failing_task()
    except ValueError:
        pass

    assert len(tracer.spans) == 1
    assert tracer.spans[0].status == "error"
    assert tracer.spans[0].error == "Test failure"
