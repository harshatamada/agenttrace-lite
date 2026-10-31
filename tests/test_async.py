
import asyncio
from agenttrace_lite import Tracer


def test_async_function_tracing(tmp_path):
    output = tmp_path / "async_traces.jsonl"
    tracer = Tracer(output=str(output))

    @tracer.trace
    async def async_agent():
        await asyncio.sleep(0.01)
        return "async result"

    result = asyncio.run(async_agent())

    assert result == "async result"
    assert len(tracer.spans) == 1
    assert tracer.spans[0].name == "async_agent"
    assert tracer.spans[0].status == "ok"


def test_nested_async_spans(tmp_path):
    output = tmp_path / "nested_async.jsonl"
    tracer = Tracer(output=str(output))

    @tracer.trace
    async def child_agent():
        await asyncio.sleep(0.01)
        return "child"

    @tracer.trace
    async def parent_agent():
        result = await child_agent()
        return result

    result = asyncio.run(parent_agent())

    assert result == "child"
    assert len(tracer.spans) == 2

    parent = next(s for s in tracer.spans if s.name == "parent_agent")
    child = next(s for s in tracer.spans if s.name == "child_agent")

    assert parent.trace_id == child.trace_id
    assert child.parent_span_id == parent.span_id
    assert parent.status == "ok"
    assert child.status == "ok"
