from agenttrace_lite import Tracer


def test_filter_by_name(tmp_path):
    tracer = Tracer(output=str(tmp_path / "test.jsonl"))

    with tracer.span("llm_call"):
        pass

    with tracer.span("tool_call"):
        pass

    result = tracer.get_spans(name="llm_call")

    assert len(result) == 1
    assert result[0].name == "llm_call"


def test_filter_by_status(tmp_path):
    tracer = Tracer(output=str(tmp_path / "test.jsonl"))

    with tracer.span("success"):
        pass

    try:
        with tracer.span("failure"):
            raise ValueError("error")
    except ValueError:
        pass

    result = tracer.get_spans(status="error")

    assert len(result) == 1
    assert result[0].name == "failure"


def test_filter_by_trace_id(tmp_path):
    tracer = Tracer(output=str(tmp_path / "test.jsonl"))

    with tracer.span("parent") as parent:
        with tracer.span("child"):
            pass

    result = tracer.get_spans(trace_id=parent.trace_id)

    assert len(result) == 2


def test_combined_filters(tmp_path):
    tracer = Tracer(output=str(tmp_path / "test.jsonl"))

    with tracer.span("llm_call"):
        pass

    try:
        with tracer.span("llm_call"):
            raise RuntimeError("failure")
    except RuntimeError:
        pass

    result = tracer.get_spans(
        name="llm_call",
        status="error"
    )

    assert len(result) == 1


def test_get_all_spans(tmp_path):
    tracer = Tracer(output=str(tmp_path / "test.jsonl"))

    with tracer.span("one"):
        pass

    with tracer.span("two"):
        pass

    assert len(tracer.get_spans()) == 2