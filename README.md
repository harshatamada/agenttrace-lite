# AgentTrace Lite

A lightweight, local-first observability SDK for AI agents. Track execution, nested spans, errors, and execution time with simple Python decorators or context managers.

## Features

- Sync and async function tracing
- Nested spans
- Error tracking
- Execution time measurement
- Custom span attributes
- JSONL trace export
- CLI for viewing and filtering traces

## Installation

```bash
pip install agenttrace-lite
```

## Quick Start

```python
from agenttrace_lite import Tracer

tracer = Tracer(service_name="my-ai-agent")

@tracer.trace
def run_agent():
    return "Hello, AI!"

run_agent()
tracer.flush()
```

## Context Manager

```python
with tracer.span("llm_call") as span:
    span.set_attribute("model", "gpt")
```

## View Traces

```bash
agenttrace traces
agenttrace traces --status error
agenttrace traces --name llm_call
```

## License

MIT
