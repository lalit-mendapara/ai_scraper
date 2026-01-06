import os
from langchain_openai import ChatOpenAI
from src.graph import app 
from langfuse.langchain import CallbackHandler
from config import (
    OPENROUTER_API_KEY, 
    OPENROUTER_BASE_URL, 
    OPENROUTER_MODEL_NAME, 
    LANGFUSE_BASE_URL,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY
)

os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_BASE_URL

# 1. Initialize the LLM
llm = ChatOpenAI(
    model_name=OPENROUTER_MODEL_NAME,
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL
)

# 2. Initialize the Langfuse Callback Handler
# This handler will automatically capture all traces from your LangGraph execution.
langfuse_handler = CallbackHandler()

def start_task():
    print("🤖 Virtual Assistant Started. You can search, filter, or ask any question.")
    first_query = input("\n👤 You: ")
    
    # 3. Add the Langfuse handler to the config dictionary
    # This allows LangGraph to send telemetry data to your Langfuse dashboard.
    config = {
        "configurable": {"thread_id": "session_001"}, 
        "callbacks": [langfuse_handler], # Tracing enabled here
        "recursion_limit": 100 
    }
    
    print("\n🚀 Assistant is processing your request...")
    
    # Invoke the graph. It will run in a relational loop until 'done'.
    # All steps, including tool calls and LLM prompts, will now be visible in Langfuse.
    app.invoke({"query": first_query}, config=config)

if __name__ == "__main__":
    start_task()