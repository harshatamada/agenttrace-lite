
import asyncio
from agenttrace_lite import Tracer


def test_concurrent_agents_have_separate_traces(tmp_path):
    output = tmp_path / "concurrent.jsonl"
    tracer = Tracer(output=str(output))

    @tracer.trace
    async def agent(task_id):
        await asyncio.sleep(0.02)
        return task_id

    async def main():
        return await asyncio.gather(
            agent("A"),
            agent("B"),
            agent("C"),
        )

    results = asyncio.run(main())

    assert results == ["A", "B", "C"]
    assert len(tracer.spans) == 3

    trace_ids = {span.trace_id for span in tracer.spans}

    # Each independent agent should have its own trace.
    assert len(trace_ids) == 3

    assert all(span.status == "ok" for span in tracer.spans)


def test_concurrent_children_share_parent_trace(tmp_path):
    output = tmp_path / "concurrent_children.jsonl"
    tracer = Tracer(output=str(output))

    @tracer.trace
    async def child(task_id):
        await asyncio.sleep(0.02)
        return task_id

    @tracer.trace
    async def parent():
        return await asyncio.gather(
            child("A"),
            child("B"),
        )

    asyncio.run(parent())

    assert len(tracer.spans) == 3

    parent_span = next(
        span for span in tracer.spans
        if span.name == "parent"
    )

    children = [
        span for span in tracer.spans
        if span.name == "child"
    ]

    assert len(children) == 2

    for span in children:
        assert span.trace_id == parent_span.trace_id
        assert span.parent_span_id == parent_span.span_id
