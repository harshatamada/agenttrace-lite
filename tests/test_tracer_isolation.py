
from agenttrace_lite import Tracer


def test_separate_tracers_do_not_share_context(tmp_path):
    tracer_a = Tracer(output=str(tmp_path / "a.jsonl"))
    tracer_b = Tracer(output=str(tmp_path / "b.jsonl"))

    @tracer_b.trace
    def task_b():
        return "B"

    @tracer_a.trace
    def task_a():
        task_b()
        return "A"

    task_a()

    span_a = next(s for s in tracer_a.spans if s.name == "task_a")
    span_b = next(s for s in tracer_b.spans if s.name == "task_b")

    # Tracer B should start an independent trace,
    # not become a child of Tracer A.
    assert span_b.trace_id != span_a.trace_id
    assert span_b.parent_span_id is None
