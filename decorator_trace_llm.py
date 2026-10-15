"""
Langfuse API Level 2: Decorator-based (@observe())

This approach uses decorators to automatically create traces and spans.
Nested function calls automatically create nested spans.
"""

from dotenv import load_dotenv
from langfuse.openai import (
    OpenAI,
)  # drop-in wrapper: auto-records model, usage and cost

from langfuse import Langfuse, observe, propagate_attributes

load_dotenv()
client = OpenAI()
langfuse = Langfuse()
PROJECT_NAME = "decorator_trace_llm"


@observe()
def calculator(expression: str) -> str:
    """Single calculation - becomes a child span when called from another @observe function."""
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a very accurate calculator. You output only the result of the calculation.",
            },
            {"role": "user", "content": expression},
        ],
    )
    return completion.choices[0].message.content


@observe()  # Nested function = nested span
def process_calculations(expressions: list[str]) -> list[str]:
    """Process multiple calculations - each calculator() call becomes a child span."""
    results = []
    for expression in expressions:
        result = calculator(expression)  # Each call becomes a child span
        results.append(f"{expression} = {result}")
    return results


if __name__ == "__main__":
    expressions = ["123 + 456", "789 * 2", "100 / 4"]

    # Wrap the root call so the root span and all children inherit these attributes
    # (user_id, tags and metadata show up as real Langfuse fields, not plain metadata keys)
    with propagate_attributes(
        user_id="user_123",
        tags=["calculator", "math"],
        metadata={"project": PROJECT_NAME},
    ):
        results = process_calculations(expressions)

    print("\033[32mResults:\033[0m")
    for i, result in enumerate(results):
        print(f"- {i + 1}. {result}")

    # Ensure data is sent to Langfuse
    langfuse.flush()
