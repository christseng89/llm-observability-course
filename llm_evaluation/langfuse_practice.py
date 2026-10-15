import re
from datetime import datetime

from dotenv import load_dotenv

from common import print_section

load_dotenv()

from langfuse.langchain import CallbackHandler
from src.agents import get_agent
from src.pipeline import run_ingestion

from langfuse import get_client, propagate_attributes

run_ingestion()

client = get_client()
handler = CallbackHandler()
agent = get_agent()
PROJECT_NAME = "LangFuse RAG Chatbot Demo"

QUESTIONS = [
    "Which accounts are active in North America",
    "What is the weather in Paris?",
]


session_id = f"chatbot-demo-{datetime.now():%Y%m%d-%H%M%S}"


# --------------- SESSION --------------

with propagate_attributes(
    session_id=session_id,
    tags=["rag-chatbot-demo"],
    user_id="demo-user",
    metadata={"project": PROJECT_NAME},
):
    print_section("Running questions through the agent")

    for question in QUESTIONS:
        print(f"\033[92mQuestion: {question}\033[0m")
        # TRACE -----
        with client.start_as_current_observation(
            name=f"question: {question}", as_type="span"
        ) as trace:
            # -------- SPAN AND GENERATION ------------
            result = agent.invoke(
                {"messages": [{"role": "user", "content": question}]},
                config={"callbacks": [handler]},
            )
            answer = result["messages"][-1].content
            sentences = re.split(r"(?<=[.!?])\s+", answer.strip())
            answer_preview = " ".join(sentences[:5])
            print(f"\033[94mAnswer Preview:\033[0m\n{answer_preview}")

            trace.update(input=question, output=answer)
            trace_id = client.get_current_trace_id()

client.flush()
