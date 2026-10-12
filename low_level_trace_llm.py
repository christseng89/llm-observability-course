"""
Langfuse API Level 4: Low-level SDK (Langfuse v4)

This approach gives you maximum control over everything:
- Custom timing
- Scores and evaluations
- Events for debugging
- Manual span/generation management
"""

from langfuse import Langfuse, propagate_attributes
from langfuse.openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI()
langfuse = Langfuse()

expression = "123 + 456 * 2"
name = "low_level"
messages = [
    {
        "role": "system",
        "content": "You are a very accurate calculator. You output only the result of the calculation.",
    },
    {"role": "user", "content": expression},
]

# propagate_attributes must wrap ALL spans/generations: only observations
# created inside this context inherit the attributes.
with propagate_attributes(
    user_id="user_123",
    tags=["calculator", name],
    metadata={"project": name + "_project"},
):
    # Create root span - this creates a new trace automatically
    root_span = langfuse.start_observation(
        name=name + "_calculator",
        input={"expression": expression},
    )

    # Get the trace_id for later use (scores)
    trace_id = root_span.trace_id

    # Create a child span for preprocessing
    preprocessing_span = root_span.start_observation(
        name=name + "_preprocessing",
        input={"raw_expression": expression},
    )
    # Simulate preprocessing work so the span is visible on the timeline
    time.sleep(0.2)
    preprocessing_span.update(
        output={"validated_expression": expression, "status": "valid"},
    )

    # End the preprocessing span before the LLM call
    preprocessing_span.end()

    # Start the generation BEFORE the LLM call so its span covers the real call duration
    generation = root_span.start_observation(
        name=name + "_llm_calculation",
        as_type="generation",
        model="gpt-4o-mini",
        model_parameters={"temperature": 1.0},
        input=messages,
    )
    start_time = time.time()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    end_time = time.time()
    result = completion.choices[0].message.content

    # Update with output and usage, then end
    generation.update(
        output=result,
        usage_details={
            "input": completion.usage.prompt_tokens,
            "output": completion.usage.completion_tokens,
            "total": completion.usage.total_tokens,
        },
        level="DEFAULT",  # Options: "DEBUG", "DEFAULT", "WARNING", "ERROR"
        status_message="Calculation completed successfully",
    )

    # End the generation span
    generation.end()

    # Create an event for debugging/logging (within current context)
    event = root_span.create_event(
        name=name + "_complete",
        input={"expression": expression},
        output={"result": result},
        metadata={"duration_ms": (end_time - start_time) * 1000},
    )

    # End the root span with final output
    root_span.update(
        output={"result": result},
        metadata={"duration_ms": (end_time - start_time) * 1000},
    )

    # End the root span to close the trace
    root_span.end()

# Add a score to evaluate the trace
langfuse.create_score(
    trace_id=trace_id,
    name="accuracy",
    value=1.0,
    comment="Correct calculation verified",
)

print(f"\033[32mExpression: {expression}\033[0m")  # ANSI green
print(f"- Result: {result}")
print(f"- Duration: {(end_time - start_time) * 1000:.2f}ms")
print(f"- Tokens used: {completion.usage.total_tokens}")
print(f"- Trace ID: {trace_id}")

# Ensure data is sent to Langfuse before script exits
langfuse.flush()
