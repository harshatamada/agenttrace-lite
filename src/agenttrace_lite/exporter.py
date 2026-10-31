
import json
from pathlib import Path


class JSONLExporter:

    def __init__(self, output="agenttrace_traces.jsonl"):
        self.output = Path(output)

    def export(self, spans):
        """Append spans to a JSONL file."""

        self.output.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.output.open("a", encoding="utf-8") as file:

            for span in spans:
                record = span.to_dict()

                file.write(
                    json.dumps(record) + "\n"
                )
