import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

load_dotenv(dotenv_path='../.env')

# 1. Define State
class MultiAgentState(TypedDict):
    topic: str
    research_notes: str
    draft_article: str
    review_comments: str

# 2. Define Node Agents
def researcher_node(state: MultiAgentState):
    print("--- 🕵️ Researcher Node Running ---")
    topic = state["topic"]
    # In a real scenario, this agent would have a DuckDuckGo web search tool!
    # For this project, we'll just have the LLM simulate research.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = f"You are a researcher. Provide 3 factual bullets about {topic}."
    
    result = llm.invoke([SystemMessage(content=prompt)])
    return {"research_notes": result.content}

def writer_node(state: MultiAgentState):
    print("--- ✍️ Writer Node Running ---")
    notes = state["research_notes"]
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = f"You are a blog writer. Write a short, engaging 2-paragraph blog post based exclusively on these notes:\n{notes}"
    
    result = llm.invoke([SystemMessage(content=prompt)])
    return {"draft_article": result.content}

def editor_node(state: MultiAgentState):
    print("--- 📝 Editor Node Running ---")
    draft = state["draft_article"]
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = f"You are a strict editor. Review the article below and provide 1 sentence of constructive criticism on how to improve it. \nArticle:\n{draft}"
    
    result = llm.invoke([SystemMessage(content=prompt)])
    return {"review_comments": result.content}

def main():
    print("🚀 Starting Multi-Agent Collaboration Workflow")

    # 3. Build Graph
    builder = StateGraph(MultiAgentState)

    builder.add_node("researcher", researcher_node)
    builder.add_node("writer", writer_node)
    builder.add_node("editor", editor_node)

    # 4. Define linear collaborative flow
    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "editor")
    builder.add_edge("editor", END)

    graph = builder.compile()

    # 5. Run Workflow
    initial_state = {"topic": "The history of the Python programming language"}
    
    print(f"\n[Topic: {initial_state['topic']}]\n")
    final_output = graph.invoke(initial_state)

    print("\n================ FINAL REPORT ================")
    print("\n--- 📚 Research Notes ---")
    print(final_output.get("research_notes", "None"))
    
    print("\n--- 📰 Draft Article ---")
    print(final_output.get("draft_article", "None"))
    
    print("\n--- 🔍 Editor Feedback ---")
    print(final_output.get("review_comments", "None"))
    print("==============================================")

    print("\n--- 🧠 Why we did this ---")
    print("By splitting tasks among specialized personas (System Prompts) and connecting")
    print("them in a graph, we get exponentially better results than asking a single LLM")
    print("to 'research, write, and critique' all at once. This multi-agent paradigm")
    print("is how the world's most capable AI software systems are built.")

if __name__ == "__main__":
    main()
