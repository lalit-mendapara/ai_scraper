import os
from config import OPENROUTER_API_KEY,OPENROUTER_BASE_URL,OPENROUTER_MODEL_NAME
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict
from src.scraper import run_scraper

# define data structure that ai 'remembers'
class AgentState(TypedDict):
    url:str
    raw_text:str
    summary:str

#1. Node: Scrape the data 
def scrape_node(state:AgentState):
    data= run_scraper(state['url'])
    return {'raw_text':data}

#2. Node: analyze with openrouter
def analyze_node(state:AgentState):
    llm = ChatOpenAI(
        model_name = OPENROUTER_MODEL_NAME,
        openai_api_key = OPENROUTER_API_KEY,
        openai_api_base = OPENROUTER_BASE_URL,
        default_headers={"X-Title":"AI Scraper"}
    )

    prompt = f"Summarise the following web content in 2 sentences: {state['raw_text']}"
    response = llm.invoke(prompt)
    return {"summary":response.content}

#Build the logic Flow
workflow= StateGraph(AgentState)
workflow.add_node("scraper",scrape_node)
workflow.add_node("analyzer",analyze_node)

workflow.set_entry_point("scraper")
workflow.add_edge("scraper","analyzer")
workflow.add_edge("analyzer",END)

app = workflow.compile()
