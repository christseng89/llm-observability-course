# model_router.py
"""
Smart Model Router
Automatically routes requests to the most cost-effective model
"""

from enum import Enum
import re
from dotenv import load_dotenv

# Integration with observability
from langfuse import observe, get_client, propagate_attributes
from anthropic import Anthropic
from langfuse.openai import OpenAI

load_dotenv()

langfuse = get_client()

# Initialize clients
anthropic_client = Anthropic()
openai_client = OpenAI()

class TaskType(Enum):
    SIMPLE = "simple"  # Yes/no, classification
    MODERATE = "moderate"  # Summarization, extraction
    COMPLEX = "complex"  # Analysis, reasoning
    CODE = "code"  # Code generation
    CREATIVE = "creative"  # Creative writing
    RESEARCH = "research"  # Current or latest information


# Model tiers (cheapest first)
# RESEARCH_MODEL = "gpt-6.1-sol"  # $2.00 / $10.00
MODELS = {
    TaskType.SIMPLE: "claude-haiku-5-5",  # $0.10 / $0.50
    TaskType.MODERATE: "gpt-4o-mini",  # $0.15 / $0.60
    TaskType.CODE: "claude-sonnet-5-5",  # $2.00 / $10.00
    TaskType.COMPLEX: "gpt-6.1-sol",  # $2.00 / $10.00
    TaskType.CREATIVE: "gpt-6.1-sol",  # $2.00 / $10.00
    TaskType.RESEARCH: "gpt-6.1-sol",
}

PROJECT_NAME = "Smart Model Router"

class ModelRouter:
    """Route requests to optimal models based on task analysis."""

    def routed_classify_task(self, prompt: str) -> TaskType:
        """Analyze prompt to determine task type."""

        prompt_lower = prompt.lower()

        # Simple patterns - yes/no, classification
        simple_patterns = [
            r"\b(yes or no)\b",
            r"\b(true or false)\b",
            r"\b(classify|categorize)\b",
            r"^is (this|it|the)",
            r"\b(which one|choose|select)\b",
        ]
        for pattern in simple_patterns:
            if re.search(pattern, prompt_lower):
                return TaskType.SIMPLE

        # Code patterns
        code_patterns = [
            r"\b(write|create|generate|fix|debug).*(code|function|class|script)\b",
            r"\b(python|javascript|typescript|java|rust)\b",
            r"```",  # Code blocks in prompt
        ]
        for pattern in code_patterns:
            if re.search(pattern, prompt_lower):
                return TaskType.CODE

        # Current-information patterns require web search rather than only
        # the model's training knowledge.
        research_patterns = [
            r"\b(latest|recent|newest|current|today|this year)\b.*\b(research|paper|study|news|development)\b",
            r"\b(research|paper|study|news|development)\b.*\b(latest|recent|newest|current)\b",
        ]
        for pattern in research_patterns:
            if re.search(pattern, prompt_lower):
                return TaskType.RESEARCH

        # Complex reasoning patterns
        complex_patterns = [
            r"\b(analyze|evaluate|compare|critique)\b",
            r"\b(why|how).*(work|happen|cause)\b",
            r"\b(pros and cons|trade-?offs)\b",
            r"\b(explain.*(detail|depth))\b",
        ]
        for pattern in complex_patterns:
            if re.search(pattern, prompt_lower):
                return TaskType.COMPLEX

        # Creative patterns
        creative_patterns = [
            r"\b(write|create|compose).*(story|poem|essay|blog)\b",
            r"\b(creative|imaginative|original)\b",
        ]
        for pattern in creative_patterns:
            if re.search(pattern, prompt_lower):
                return TaskType.CREATIVE

        # Default to moderate
        return TaskType.MODERATE

    def route(self, prompt: str, override_model: str | None = None) -> str:
        """Get the optimal model for a prompt."""

        if override_model:
            return override_model

        task_type = self.routed_classify_task(prompt)
        print(f"\033[38;5;130mRouting prompt to task type: {task_type.value}, model: {MODELS[task_type]}\033[0m")
        return MODELS[task_type]


router = ModelRouter()

def routed_call_claude(prompt: str, model: str):
    """Call Claude API."""
    messages = [{"role": "user", "content": prompt}]

    with langfuse.start_as_current_observation(
        name="claude-routing-generation",
        as_type="generation",
        model=model,
        input=messages,
        model_parameters={"max_tokens": 1024},
    ) as generation:
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=1024,
            messages=messages,
        )
        response_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        generation.update(
            model=response.model,
            output=response_text,
            usage_details={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
            },
        )

    return response_text


def routed_call_openai(prompt: str, model: str):
    """Call OpenAI API."""
    if model == MODELS[TaskType.RESEARCH]:
        response = openai_client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            input=prompt,
        )
        return response.output_text

    response = openai_client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


@observe()
def routed_llm_call(prompt: str, override_model: str = None) -> str:
    """LLM call with automatic model routing."""

    selected_model = router.route(prompt, override_model)
    task_type = router.routed_classify_task(prompt)

    langfuse.update_current_span(
        metadata={
            "task_type": task_type.value,
            "routed_model": selected_model,
        }
    )

    # Use the provider-appropriate function
    if "claude" in selected_model:
        return routed_call_claude(prompt, model=selected_model)
    else:
        return routed_call_openai(prompt, model=selected_model)


if __name__ == "__main__":
    # Test different prompts to see routing in action
    with propagate_attributes(
        user_id="user_123",
        tags=["model-routing", "cost-optimization"],
        metadata={"project": PROJECT_NAME},
    ):

        questions = [
            "Is 2 + 2 = 4? Yes or no",
            "Write a Python function to sort a list",
            "Summarize the key points of the latest Agentic AI research paper in Chinese",
            "Write a short story about a robot learning to love within 100 words",
        ]

        for question in questions:
            print(f"\033[92m\nPrompt: {question}\033[0m")
            response = routed_llm_call(question)
            print(f"Response: {response}")

    langfuse.flush()
