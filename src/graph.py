from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. State Definition: The "Shared Memory" of the assistant
class AgentState(TypedDict):
    query: str
    raw_data: List[dict]
    filtered_data: List[dict]
    answer: str
    next_action: str 

# 2. Node Functions
def router_node(state: AgentState):
    """Initial check: Is this a search or a fact-based question?"""
    from main import llm
    prompt = f"Categorize query: 'scrape' for products or 'general' for facts. Query: {state['query']}. Reply with one word."
    decision = llm.invoke(prompt).content.strip().lower()
    return {"intent": "general" if "general" in decision else "scrape"}

def scraper_node(state: AgentState):
    """Playwright worker: Fills memory with Amazon products."""
    from .scraper import scrape_amazon_node
    data = scrape_amazon_node(state)
    return {"raw_data": data["raw_data"], "filtered_data": data["raw_data"], "answer": ""}

def general_node(state: AgentState):
    """General Knowledge: Answers any question using the LLM."""
    from main import llm
    res = llm.invoke(state["query"])
    return {"answer": res.content}

def analyzer_node(state: AgentState):
    """
    THE ASSISTANT HUB: Shows status and waits for your next command.
    It clears old answers so you don't see them twice.
    """
    from main import llm
    
    if state.get("answer"):
        print(f"\n🤖 ASSISTANT: {state['answer']}")
    
    data = state.get("filtered_data", [])
    if data:
        print(f"\n--- 📱 CURRENT PRODUCTS ({len(data)} items) ---")
        for item in data[:2]: print(f"- {item['name']}")
    
    user_req = input("\n💬 Your Command (search, filter, zip, ask anything, or 'done'): ")
    
    # AI decides what the user wants to do next dynamically
    prompt = f"User said: '{user_req}'. Pick action: 'scrape', 'filter', 'zip', 'general', or 'exit'. One word."
    action = llm.invoke(prompt).content.strip().lower()
    
    return {"query": user_req, "next_action": action, "answer": ""}

def filter_node(state: AgentState):
    """Filters the existing product list in memory."""
    from main import llm
    import json
    if not state.get("filtered_data"):
        return {"answer": "⚠️ No products to filter yet. Search for something first!"}
    
    prompt = f"Filter JSON list based on '{state['query']}': {json.dumps(state['filtered_data'][:15])}"
    response = llm.invoke(prompt)
    try:
        content = response.content.split("```json")[-1].split("```")[0].strip()
        return {"filtered_data": json.loads(content), "answer": "✅ Filter applied."}
    except:
        return {"answer": "❌ I couldn't process that filter."}

def archiver_node(state: AgentState):
    """Creates the ZIP file in the outputs folder."""
    from .scraper import zip_exporter_node
    return zip_exporter_node(state)

# 3. Dynamic Routing: Enables jumping between any task at any time
def route_logic(state: AgentState):
    act = state.get("next_action")
    if act == "exit" or "done" in state["query"].lower(): return END
    if act == "scrape": return "scraper" 
    if act == "zip": return "archiver_node"
    if act == "filter": return "filter_node"
    return "general_node"

# 4. Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("scraper", scraper_node)
workflow.add_node("general_node", general_node)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("filter_node", filter_node)
workflow.add_node("archiver_node", archiver_node)

workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", lambda x: "general_node" if x["intent"] == "general" else "scraper")
workflow.add_edge("scraper", "analyzer")
workflow.add_edge("general_node", "analyzer")
workflow.add_conditional_edges("analyzer", route_logic)
workflow.add_edge("filter_node", "analyzer")
workflow.add_edge("archiver_node", "analyzer")

memory = MemorySaver() # Keeps memory alive across turns
app = workflow.compile(checkpointer=memory)