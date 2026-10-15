# instrumented_llm.py
"""
Production-Ready LLM Wrapper with Observability
Use this as a starting point for your applications

Updated for Langfuse Python SDK v4 (Decorator-based API)
"""

import time
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from langfuse.openai import OpenAI

from common import print_section
from langfuse import Langfuse, observe, propagate_attributes

load_dotenv()

# Initialize clients
anthropic_client = Anthropic()
openai_client = OpenAI()
langfuse = Langfuse()

PROJECT_NAME = "instrumented_llm"


@dataclass
class LLMResponse:
    """Structured response from LLM calls."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    duration_ms: float
    cost: float


# Token pricing (per 1M tokens) - Update as needed
PRICING = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-5-5": {"input": 0.25, "output": 1.25},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


def calculate_cost_details(
    model: str, input_tokens: int, output_tokens: int
) -> dict[str, float] | None:
    """Return cost components, or None so Langfuse can infer unknown pricing."""
    pricing = PRICING.get(model)
    if pricing is None:
        return None
    return {
        "input": input_tokens / 1_000_000 * pricing["input"],
        "output": output_tokens / 1_000_000 * pricing["output"],
    }


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on token usage."""
    return sum(
        (calculate_cost_details(model, input_tokens, output_tokens) or {}).values()
    )


def build_response(
    content: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    start: float,
    cost_details: dict[str, float] | None,
) -> LLMResponse:
    """Normalize provider results and elapsed time."""
    return LLMResponse(
        content=content,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model=model,
        duration_ms=(time.perf_counter() - start) * 1000,
        cost=sum((cost_details or {}).values()),
    )


def print_response(label: str, response: LLMResponse) -> None:
    """Print a response with a yellow heading and consistent usage details."""
    print(f"\n\033[33m{label} Response:\033[0m \n{response.content}")
    print(f"\n- Tokens: {response.input_tokens} in, {response.output_tokens} out")
    print(f"- Model: {response.model}")
    print(f"- Cost: ${response.cost:.6f}")
    print(f"- Duration: {response.duration_ms:.0f}ms")


@observe()  # Span for the call to Claude
def instr_call_claude(
    prompt: str,
    model: str = "claude-haiku-5-5",
    system: str | None = None,
    max_tokens: int = 1024,
    metadata: dict[str, Any] | None = None,
) -> LLMResponse:

    start = time.perf_counter()
    messages = [{"role": "user", "content": prompt}]

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }

    if system:
        kwargs["system"] = system

    # Generation span with model-specific metadata and cost details
    with langfuse.start_as_current_observation(
        as_type="generation",
        name="Claude-generation",
        model=model,
        input=messages,
        model_parameters={"max_tokens": max_tokens, "system": system},
        metadata=metadata,
    ) as generation:
        response = anthropic_client.messages.create(**kwargs)

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost_details = calculate_cost_details(model, input_tokens, output_tokens)
        content = "".join(
            block.text for block in response.content if block.type == "text"
        )
        result = build_response(
            content,
            response.model,
            input_tokens,
            output_tokens,
            start,
            cost_details,
        )

        generation.update(
            model=response.model,
            output=result.content,
            usage_details={"input": input_tokens, "output": output_tokens},
            cost_details=cost_details,
            metadata={
                **(metadata or {}),
                "duration_ms": result.duration_ms,
                "stop_reason": response.stop_reason,
            },
        )

    return result


@observe()
def instr_call_openai(
    prompt: str,
    model: str = "gpt-4o-mini",
    system: str | None = None,
    max_tokens: int = 1024,
    metadata: dict[str, Any] | None = None,
) -> LLMResponse:
    """Call OpenAI with full observability."""

    start = time.perf_counter()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = openai_client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
    )

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost_details = calculate_cost_details(model, input_tokens, output_tokens)
    result = build_response(
        response.choices[0].message.content,
        model,
        input_tokens,
        output_tokens,
        start,
        cost_details,
    )

    # Update current span with model-specific info using v4 API
    langfuse.update_current_span(
        metadata={
            **(metadata or {}),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": result.duration_ms,
            "cost": result.cost,
        },
    )

    return result


@observe()
def instr_compare(prompt: str) -> dict:
    """
    Compare responses from Claude and OpenAI for the same prompt.
    Each call becomes a child span in the trace.
    """
    claude_response = instr_call_claude(prompt)
    openai_response = instr_call_openai(prompt)

    langfuse.update_current_span(
        metadata={"comparison": True},
    )

    return {
        "claude": claude_response,
        "openai": openai_response,
    }


# Example usage
if __name__ == "__main__":
    print_section("Langfuse Observability Example: Instrumented LLM Calls")
    with propagate_attributes(
        user_id="user_123",
        tags=["observability", "theory of relativity"],
        metadata={"project": PROJECT_NAME},
    ):
        # # Simple call - creates a trace with one span
        # response = instr_call_claude("What is observability in 2 sentences?")
        # print_response("Claude", response)

        query = "Explain the theory of relativity in simple terms in Chinese."
        response = instr_compare(query)

        # print(f"Response: {response.content}")
        print(f"\033[32mQuery: {query}\033[0m")

        print_response("OpenAI", response["openai"])
        print_response("Claude", response["claude"])

        # IMPORTANT: Always flush in short-lived scripts to ensure data is sent
        langfuse.flush()
