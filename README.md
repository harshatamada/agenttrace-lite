# AgentTrace Lite

A lightweight, local-first observability SDK for AI agents. Monitor function execution, nested spans, errors, and execution time with minimal code changes.

## Features

- Sync and async function tracing
- Nested spans and parent-child relationships
- Automatic error tracking
- Execution time measurement
- Custom span attributes
- Local JSONL trace export
- CLI for viewing and filtering traces
- Thread-safe trace collection
- Context manager support

## Installation

```bash
pip install agenttrace-lite
```

## Quick Start

Integrate AgentTrace Lite into your existing Python application in just a few lines.

```python
# ==========================================
# AgentTrace Lite — Add these lines
# ==========================================

from agenttrace_lite import Tracer

tracer = Tracer(service_name="my-ai-agent")


# ==========================================
# Developer's existing application code
# ==========================================

@tracer.trace  # AgentTrace: add this decorator
def run_agent(prompt):

    # Developer: your existing AI/LLM logic goes here
    response = your_llm_client.generate(prompt)

    return response


# ==========================================
# Developer's existing code
# ==========================================

result = run_agent("Explain RAG")
print(result)


# ==========================================
# AgentTrace Lite — Add this line
# ==========================================

tracer.flush()  # Export collected traces
```

**That's it!** Your function execution is now traced.

> `your_llm_client.generate(prompt)` is a placeholder for your own LLM integration. Replace it with your actual Gemini, OpenAI, or other model call. It is not provided by AgentTrace Lite.

## How It Works

1. Initialize a `Tracer` with your application name.
2. Add `@tracer.trace` to the function you want to monitor.
3. Run your application as usual.
4. Call `tracer.flush()` to export the collected traces.

AgentTrace automatically records:

- Function name
- Execution duration
- Success or error status
- Trace ID
- Parent span ID
- Service name

Your application logic remains unchanged.

## Trace an LLM Call

Example using the Google Gemini SDK:

```python
# ==========================================
# AgentTrace Lite
# ==========================================

from agenttrace_lite import Tracer

tracer = Tracer(service_name="gemini-agent")


# ==========================================
# Developer's Gemini application code
# ==========================================

from google import genai

client = genai.Client()


@tracer.trace
def ask_gemini(prompt):

    # Developer's actual Gemini API call
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# Developer runs their application
# ==========================================

answer = ask_gemini("Explain AI agents in simple terms")
print(answer)


# ==========================================
# AgentTrace Lite
# ==========================================

tracer.flush()
```

AgentTrace records the execution of `ask_gemini`, including its duration and status.

## Context Manager

Use context managers when you want to trace a specific operation inside a function.

```python
with tracer.span("llm_call") as span:

    # AgentTrace: attach custom metadata
    span.set_attribute("model", "gemini-2.5-flash")

    # Developer: existing LLM call
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain RAG"
    )
```

Custom attributes are stored alongside the span data.

## Async Function Tracing

AgentTrace also supports asynchronous Python functions.

```python
@tracer.trace
async def run_agent(prompt):

    # Developer's existing async logic
    response = await your_async_llm_call(prompt)

    return response
```

## View Traces

After running your application, view the collected traces using the CLI.

```bash
agenttrace traces
```

### Filter by status

```bash
agenttrace traces --status error
```

Available statuses:

- `ok`
- `error`
- `running`

### Filter by function name

```bash
agenttrace traces --name llm_call
```

## Trace Storage

AgentTrace Lite stores traces locally in JSONL format.

Default output:

```text
agenttrace_traces.jsonl
```

Each line represents an individual span containing information such as:

```json
{
  "trace_id": "unique-trace-id",
  "span_id": "unique-span-id",
  "parent_span_id": null,
  "name": "run_agent",
  "duration_ms": 125.42,
  "status": "ok",
  "attributes": {},
  "error": null,
  "service_name": "my-ai-agent"
}
```

This is an illustrative example of the trace structure.

## Privacy & Design

- Local-first observability
- No external telemetry server required
- Traces stored on your local machine
- No automatic transmission of application data

## License

MIT License
