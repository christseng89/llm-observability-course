from langfuse import observe, get_client #, Langfuse
from dotenv import load_dotenv
# import os


load_dotenv()

# # Replace the following lines with get_client() if you have already set up the Langfuse client in your environment
# langfuse = Langfuse(
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     base_url=os.getenv("LANGFUSE_BASE_URL")
# )


@observe
def verify_connection():
    test_generation()

    # get client and flush it
    client = get_client()
    client.flush()

    print("Connection to Langfuse is successful!")
    print("check your dashboard at https://us.cloud.langfuse.com/")


@observe
def test_generation():
    """A simple test generation function to verify Langfuse connection."""

    # The observe decorator will automatically log this function call to Langfuse
    return "Hello, Langfuse!"


if __name__ == "__main__":
    verify_connection()
