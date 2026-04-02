import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv(dotenv_path='../.env')

# 1. Define Custom Tools
# We use the @tool decorator. The function name and DOCSTRING are extremely 
# important because the LLM reads the docstring to understand WHEN to use the tool!

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers. Use this for math problems."""
    return a * b

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def main():
    print("🚀 Starting Basic Tools & Agents")
    
    # 2. Gather Tools
    # We combine our custom math tools with a pre-built web search tool.
    search_tool = DuckDuckGoSearchRun()
    
    tools = [search_tool, multiply, add]
    
    # 3. Initialize the LLM
    # Notice we are using gemini-1.5-pro or flash. Agents work better with models 
    # that are trained on function calling (tool use).
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # 4. Create the Agent
    # In modern LangChain, we often use LangGraph's prebuilt 'create_react_agent' 
    # to create an agent that loops: Decide -> Act -> Observe -> Decide ...
    # This manages the state of the conversation and tool calls automatically.
    agent_executor = create_react_agent(llm, tools)

    # 5. Run the Agent
    # Scenario 1: Needs Web Search
    query_search = "Who is the current CEO of Google?"
    print(f"\n--- Request: {query_search} ---")
    
    # The agent receives messages and returns a final state containing all messages
    result1 = agent_executor.invoke(
        {"messages": [{"role": "user", "content": query_search}]}
    )
    print(f"🤖 Answer: {result1['messages'][-1].content}")

    # Scenario 2: Needs Math
    query_math = "If I have 15 baskets and each has 7 apples, how many apples total?"
    print(f"\n--- Request: {query_math} ---")
    
    result2 = agent_executor.invoke(
        {"messages": [{"role": "user", "content": query_math}]}
    )
    print(f"🤖 Answer: {result2['messages'][-1].content}")

    # Scenario 3: Complex Multi-step (Search THEN Math)
    query_multi = "Take the number of wheels on a standard car, and multiply it by 55.5"
    print(f"\n--- Request: {query_multi} ---")
    
    result3 = agent_executor.invoke(
        {"messages": [{"role": "user", "content": query_multi}]}
    )
    print(f"🤖 Answer: {result3['messages'][-1].content}")

    print("\n--- 🧠 Why we did this ---")
    print("LLMs are fundamentally just text predictors. They can't do exact math reliably ")
    print("and they don't know the future / current events. By giving an LLM 'Tools', ")
    print("we upgrade it into an 'Agent'. The LLM outputs a special dictionary saying ")
    print("'Please execute tool X with args Y'. The framework executes it, feeds the ")
    print("result back to the LLM, and the LLM synthesizes the final answer. Amazing!")

if __name__ == "__main__":
    main()
