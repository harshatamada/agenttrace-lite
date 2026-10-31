import argparse
import json
from pathlib import Path


def load_traces(filepath):
    path = Path(filepath)

    if not path.exists():
        print(f"No trace file found: {filepath}")
        return []

    traces = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                try:
                    traces.append(json.loads(line))
                except json.JSONDecodeError:
                    print("Warning: Skipping invalid JSON line.")

    return traces


def main():
    parser = argparse.ArgumentParser(
        prog="agenttrace",
        description="AgentTrace Lite CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    traces_parser = subparsers.add_parser(
        "traces",
        help="View recorded traces"
    )

    traces_parser.add_argument(
        "--file",
        default="agenttrace_traces.jsonl",
        help="Path to the JSONL trace file"
    )

    traces_parser.add_argument(
        "--status",
        choices=["ok", "error", "running"],
        help="Filter traces by status"
    )

    traces_parser.add_argument(
        "--name",
        help="Filter traces by span name"
    )

    args = parser.parse_args()

    if args.command == "traces":
        traces = load_traces(args.file)

        if args.status:
            traces = [
                trace for trace in traces
                if trace.get("status") == args.status
            ]

        if args.name:
            traces = [
                trace for trace in traces
                if trace.get("name") == args.name
            ]

        if not traces:
            print("No matching traces found.")
            return

        headers = [
          "STATUS",
          "NAME",
          "DURATION (ms)",
          "SERVICE",
          "TRACE ID"
        ]

        rows = []

        for trace in traces:
            rows.append([
                 trace.get("status", "unknown").upper(),
                 trace.get("name", "unnamed"),
                 str(trace.get("duration_ms", "-")),
                 trace.get("service_name", "-"),
                 trace.get("trace_id", "-")[:8]
            ])

        column_widths = [
            max(len(headers[i]), *(len(row[i]) for row in rows))
            for i in range(len(headers))
        ]

        header_row = " | ".join(
            headers[i].ljust(column_widths[i])
            for i in range(len(headers))
        )

        separator = "-+-".join(
            "-" * width
            for width in column_widths
        )

        print(header_row)
        print(separator)

        for row in rows:
            print(
                " | ".join(
                    row[i].ljust(column_widths[i])
                    for i in range(len(row))
                )
            )

        print(f"\nTotal spans: {len(rows)}")


if __name__ == "__main__":
    main()