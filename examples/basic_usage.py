from agenttrace_lite import Tracer

tracer = Tracer(service_name="example-agent")


@tracer.trace
def retrieve_context():
    return "Context retrieved"


@tracer.trace
def generate_response():
    context = retrieve_context()

    with tracer.span("llm_call") as span:
        span.set_attribute("model", "example-model")
        response = "Hello from AgentTrace Lite!"

    return response


result = generate_response()

print(result)

tracer.flush()
print("Traces exported successfully.")