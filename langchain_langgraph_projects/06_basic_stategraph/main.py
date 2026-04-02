import os
from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv(dotenv_path='../.env')

# 1. Define the State
# In LangGraph, EVERYTHING is state passed between nodes.
# TypedDict defines what data our graph keeps track of.
# In a real app, this could contain arrays of messages, user IDs, JSON blobs, etc.
class GraphState(TypedDict):
    input_text: str
    uppercase_text: str
    sentiment: str
    final_result: str

# 2. Define the Nodes
# A node is just a python function that takes the current State, 
# modifies it, and returns the changes.

def to_uppercase_node(state: GraphState):
    print("--- 🔄 Node 1: Running Uppercase Node ---")
    original = state["input_text"]
    return {"uppercase_text": original.upper()} # Returns a partial dict to update state

def sentiment_analysis_node(state: GraphState):
    print("--- 🔄 Node 2: Running Sentiment Node ---")
    # We can use an LLM here to analyze the state!
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    msg = HumanMessage(content=f"What is the sentiment of this text? Respond only with ONE word ('Positive', 'Negative', or 'Neutral'): {state['input_text']}")
    response = llm.invoke([msg])
    return {"sentiment": response.content.strip()}

def compile_results_node(state: GraphState):
    print("--- 🔄 Node 3: Compiling Results ---")
    result = f"Text: {state['uppercase_text']} | Detected Sentiment: {state['sentiment']}"
    return {"final_result": result}

def main():
    print("🚀 Starting Basic LangGraph StateGraph")

    # 3. Build the Graph
    builder = StateGraph(GraphState)

    # Add the nodes we defined
    builder.add_node("upper", to_uppercase_node)
    builder.add_node("sentiment", sentiment_analysis_node)
    builder.add_node("compile", compile_results_node)

    # 4. Define the Edges (The Flow)
    # Start -> Upper -> Sentiment -> Compile -> End
    builder.add_edge(START, "upper")
    builder.add_edge("upper", "sentiment")
    builder.add_edge("sentiment", "compile")
    builder.add_edge("compile", END)

    # 5. Compile the Graph
    # Compiling turns our definition into a runnable object.
    graph = builder.compile()

    # 6. Run it!
    # Our initial state starts with just the input_text
    initial_state = {"input_text": "I absolutely love writing code in python. It is fantastic!"}
    
    print(f"\n[Starting Graph with text: {initial_state['input_text']}]\n")
    
    # We invoke it just like a LangChain chain
    final_output = graph.invoke(initial_state)

    print("\n--- ✅ Final State Dictionary ---")
    import json
    print(json.dumps(final_output, indent=2))
    
    print("\n--- 🧠 Why we did this ---")
    print("LangChain chains (LCEL) are like pipes: linear and strict.")
    print("LangGraph allows you to define complex workflows as state machines. ")
    print("You can have cyclic loops, conditional branching (If sentiment is bad, ")
    print("route to human support), and explicit control over exactly what code ")
    print("runs at what time. It's the standard for building complex Agents.")

if __name__ == "__main__":
    main()
