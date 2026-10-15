"""
Langfuse API Level 3: Context Manager (Langfuse v4)

This approach uses context managers to explicitly define trace hierarchy.
You have fine-grained control over spans and generations.
"""

from dotenv import load_dotenv
from langfuse.openai import OpenAI

from langfuse import Langfuse, propagate_attributes

load_dotenv()
client = OpenAI()
langfuse = Langfuse()

name = "cm_trace"
expression = "123 + 456 * 2"

SYSTEM_PROMPT = (
    "You are a very accurate calculator. "
    "Evaluate the expression following standard operator precedence "
    "(multiplication and division before addition and subtraction). "
    "Work step by step, computing each operation explicitly. "
    "Then, on the last line, write 'ANSWER: <number>' with only the final number. "
    "Example for '2 + 3 * 4':\n"
    "3 * 4 = 12\n"
    "2 + 12 = 14\n"
    "ANSWER: 14"
)
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": expression},
]

# propagate_attributes must wrap ALL spans/generations: only observations
# created inside this context inherit the attributes.
with propagate_attributes(
    user_id="user_123",
    tags=["calculator", name],
    metadata={"project": name + "_project"},
):
    # Create a trace and use context managers for spans/generations
    with langfuse.start_as_current_observation(
        name=name + "_calculator_span",
        as_type="span",  # Span
    ) as trace:
        # Add a span for preprocessing
        with langfuse.start_as_current_observation(
            name=name + "_validation_span",
            as_type="span",  # Span
        ) as validation_span:
            langfuse.update_current_span(
                input={"expression": expression},
                output={"status": "valid"},
            )

        # Wrap the LLM call in a span: langfuse.openai already creates the
        # generation (model, usage, cost) automatically as a child of it.
        with langfuse.start_as_current_observation(
            name=name + "_llm_span",
            as_type="span",  # Span
        ):
            completion = client.chat.completions.create(
                name=name + "_llm_generation",
                model="gpt-4o-mini",
                messages=messages,
                temperature=0,
            )
            raw_output = completion.choices[0].message.content
            # Take the final number from the "ANSWER: <number>" line
            result = raw_output.rsplit("ANSWER:", 1)[-1].strip()

        # Update trace with final output
        trace.update(
            input={"expression": expression},
            output={"result": result},
        )

print(f"{expression} = {result}")

# Ensure data is sent to Langfuse before script exits
langfuse.flush()
