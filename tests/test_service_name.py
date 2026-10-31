
import json
from agenttrace_lite import Tracer


def test_service_name_is_exported(tmp_path):
    output = tmp_path / "service.jsonl"

    tracer = Tracer(
        service_name="my-ai-app",
        output=str(output)
    )

    @tracer.trace
    def agent():
        return "done"

    agent()
    tracer.flush()

    with output.open() as file:
        record = json.loads(file.readline())

    assert record["service_name"] == "my-ai-app"
