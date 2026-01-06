import os
from langchain_openai import ChatOpenAI
from src.graph import app 
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL_NAME

llm = ChatOpenAI(
    model_name=OPENROUTER_MODEL_NAME,
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL
)

def start_task():
    print("🤖 Virtual Assistant Started. You can search, filter, or ask any question.")
    first_query = input("\n👤 You: ")
    
    config = {
        "configurable": {"thread_id": "session_001"}, 
        "recursion_limit": 100 
    }
    
    # Invoke the graph. It will run in a relational loop until 'done'.
    app.invoke({"query": first_query}, config=config)

if __name__ == "__main__":
    start_task()