
import pytest
from agenttrace_lite import Tracer


def test_exception_is_recorded_and_reraised(tmp_path):
    tracer = Tracer(output=str(tmp_path / "errors.jsonl"))

    @tracer.trace
    def failing_agent():
        raise ValueError("Agent failed")

    with pytest.raises(ValueError, match="Agent failed"):
        failing_agent()

    assert len(tracer.spans) == 1

    span = tracer.spans[0]

    assert span.status == "error"
    assert span.error == "Agent failed"
    assert span.end_time is not None


def test_child_failure_does_not_corrupt_parent_trace(tmp_path):
    tracer = Tracer(output=str(tmp_path / "nested_errors.jsonl"))

    @tracer.trace
    def failing_tool():
        raise RuntimeError("Tool failed")

    @tracer.trace
    def agent():
        return failing_tool()

    with pytest.raises(RuntimeError, match="Tool failed"):
        agent()

    assert len(tracer.spans) == 2

    parent = next(s for s in tracer.spans if s.name == "agent")
    child = next(s for s in tracer.spans if s.name == "failing_tool")

    assert parent.status == "error"
    assert child.status == "error"
    assert parent.trace_id == child.trace_id
    assert child.parent_span_id == parent.span_id
