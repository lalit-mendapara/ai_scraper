import uuid # Standard library to generate unique IDs
from langfuse import Langfuse, get_client
from src.graph import app
from langfuse.langchain import CallbackHandler
from config import LANGFUSE_BASE_URL, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY

# Set up Langfuse Monitoring
Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_BASE_URL
)

if get_client().auth_check():
    print("Langfuse Authenticated Successfully!")
else:
    print("Langfuse Authentication Failed. Check your keys.")

langfuse_handler = CallbackHandler()

def start_task(target_url):
    print(f"Starting AI agent for: {target_url}")

    # KEY CHANGE: Generate a unique thread ID for every run 
    # This prevents the agent from reusing old state/memory.
    unique_id = str(uuid.uuid4())
    
    # Update config to include both the thread_id and the langfuse callback
    config = {
        "configurable": {"thread_id": unique_id},
        "callbacks": [langfuse_handler]
    }

    inputs = {"url": target_url}
    
    # Invoke the graph with the new config
    result = app.invoke(inputs, config=config)

    print("\n---- FINAL SUMMARY ----")
    print(result["summary"])
    print(f"\nTask Complete. Thread ID: {unique_id}")
    print("Check Langfuse for traces.")

if __name__ == "__main__":
    start_task("https://www.geeksforgeeks.org/machine-learning/supervised-machine-learning/")
    # Test URL 2 - This will now be fresh because of the new UUID
    # start_task("")