from dotenv import load_dotenv
from langfuse import observe, get_client, propagate_attributes

from common import print_section

# Initialize OpenTelemetry instrumentation for LangChain
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

# use with any langchain component
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
LangchainInstrumentor().instrument()

PROJECT_NAME = "instrumented_langchain"
MODEL = "claude-haiku-5-5"  # or "claude-sonnet-4-6" for more complex tasks
TOPIC = "quantum computing in Chinese"


@observe(name="langchain_claude_example", as_type="span")
def langchain_claude_example():
    """Run a simple LangChain example with observability."""
    llm = ChatAnthropic(model=MODEL)
    prompt = ChatPromptTemplate.from_template("Explain {topic} in simple terms.")
    chain = prompt | llm

    # OpenTelemetry instrumentation captures this automatically
    response = chain.invoke({"topic": TOPIC})
    return response


if __name__ == "__main__":
    print_section("Langfuse Observability Example: Instrumented LangChainCalls")
    with propagate_attributes(
        user_id="user_123",
        tags=["observability", "instrumented langchain"],
        metadata={"project": PROJECT_NAME},
    ):
        response = langchain_claude_example()

        print(f"\033[32mTopic: {TOPIC}\033[0m")

        response_preview = response.text.split("\n")[
            0
        ]  # Show only the first line for brevity
        print(f"\033[33mResponse (preview):\033[0m\n{response_preview}")
        # print(response)
        get_client().flush()  # Ensure all events are sent to Langfuse
