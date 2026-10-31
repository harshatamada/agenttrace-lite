import json
import pytest

from agenttrace_lite import Tracer


def test_context_manager_creates_span(tmp_path):
    output = tmp_path / "context.jsonl"
    tracer = Tracer(output=str(output))

    with tracer.span("llm_call") as span:
        span.set_attribute("model", "gpt")

    assert span.status == "ok"
    tracer.flush()

    with output.open() as file:
        record = json.loads(file.readline())

    assert record["name"] == "llm_call"
    assert record["attributes"]["model"] == "gpt"


def test_nested_context_manager(tmp_path):
    tracer = Tracer(output=str(tmp_path / "nested.jsonl"))

    with tracer.span("agent"):
        with tracer.span("tool_call"):
            pass

    parent, child = tracer.spans

    assert child.parent_span_id == parent.span_id
    assert child.trace_id == parent.trace_id


def test_context_manager_records_error(tmp_path):
    tracer = Tracer(output=str(tmp_path / "error.jsonl"))

    with pytest.raises(ValueError):
        with tracer.span("failing_operation"):
            raise ValueError("Something went wrong")

    span = tracer.spans[0]

    assert span.status == "error"
    assert span.error == "Something went wrong"