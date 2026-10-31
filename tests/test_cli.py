import json

from agenttrace_lite.cli import load_traces


def test_missing_file(tmp_path):
    file_path = tmp_path / "missing.jsonl"

    result = load_traces(str(file_path))

    assert result == []


def test_empty_file(tmp_path):
    file_path = tmp_path / "empty.jsonl"
    file_path.write_text("")

    result = load_traces(str(file_path))

    assert result == []


def test_invalid_json_line(tmp_path):
    file_path = tmp_path / "invalid.jsonl"

    file_path.write_text(
        '{"name": "valid"}\n'
        'this is not json\n'
        '{"name": "another valid"}\n'
    )

    result = load_traces(str(file_path))

    assert len(result) == 2
    assert result[0]["name"] == "valid"


def test_multiple_flushes(tmp_path):
    from agenttrace_lite import Tracer

    output = tmp_path / "multiple.jsonl"
    tracer = Tracer(output=str(output))

    with tracer.span("first"):
        pass

    tracer.flush()

    with tracer.span("second"):
        pass

    tracer.flush()

    lines = output.read_text().strip().splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0])["name"] == "first"
    assert json.loads(lines[1])["name"] == "second"