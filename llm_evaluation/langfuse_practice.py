from datetime import datetime 
from dotenv import load_dotenv 

load_dotenv() 

from langfuse import get_client, propagate_attributes 

from langfuse.langchain import CallbackHandler 

from src.agents import get_agent   
from src.pipeline import run_ingestion  

run_ingestion() 

client = get_client()
handler = CallbackHandler() 
agent = get_agent() 


QUESTIONS = [
    "Which accounts are active in North America",
    "What is the weather in Paris?"
]


session_id = f"chatbot-demo-{datetime.now():%Y%m%d-%H%M%S}"


# --------------- SESSION --------------

with propagate_attributes(session_id=session_id, tags=["rag-chatbot-demo"]):
    for question in QUESTIONS: 
        # TRACE -----
        with client.start_as_current_observation(
            name=f"question: {question}", as_type="span"
        ) as trace:
            # -------- SPAN AND GENERATION ------------
            result = agent.invoke(
                {"message": [{"role": "user", "content": question}]},
                config={"callbacks": [handler]}
            )
            answer = result["messages"][-1].content 

            trace.update(input=question, output=answer)
            trace_id = client.get_current_trace_id() 

client.flush()             