import time
from langfuse import get_client

from dotenv import load_dotenv


load_dotenv()

langfuse = get_client()

with langfuse.start_as_current_observation(
    name="test-trace",
    as_type="span",
) as span:
    span.update(output="Testing Langfuse tracing")

start = time.perf_counter()

langfuse.flush()

elapsed = time.perf_counter() - start

print(f"Flush completed in {elapsed:.2f}s")
