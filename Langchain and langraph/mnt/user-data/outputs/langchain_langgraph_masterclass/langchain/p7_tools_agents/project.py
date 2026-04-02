"""
================================================================================
PROJECT 7: Tools & Agents — LLMs That Take Actions
================================================================================
WHAT YOU LEARN:
  - What a "tool" is and how to create custom tools
  - The @tool decorator (simplest way to make tools)
  - StructuredTool for tools with complex inputs
  - Built-in tools (DuckDuckGo, Calculator, Python REPL)
  - What an "agent" is: LLM + tools + decision loop
  - create_react_agent: ReAct pattern (Reason → Act → Observe)
  - AgentExecutor: Runs the agent loop with callbacks
  - Handling agent errors and edge cases

THE BIG IDEA — AGENTS:
  A "tool" is just a Python function the LLM can CALL.
  An "agent" is a loop:
    1. LLM THINKS about what to do (reasoning)
    2. LLM PICKS a tool and arguments (action)
    3. Tool RUNS and returns a result (observation)
    4. LLM sees the result and decides what to do next
    5. Repeat until the answer is found
  
  This is how LLMs can search the web, run code, query databases!

SECRET TIP: The most important part of a good tool is the docstring.
            The LLM reads it to decide WHEN and HOW to use the tool.
================================================================================
"""

from langchain_groq import ChatGroq
from langchain_core.tools import tool, StructuredTool   # Tool decorators
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub   # Pre-built prompts from LangChain hub
from pydantic import BaseModel, Field    # For StructuredTool input validation
from dotenv import load_dotenv
from typing import Optional
import math
import datetime
import json

load_dotenv()
llm = ChatGroq(model="llama3-8b-8192", temperature=0)


# ── LESSON 1: Creating Tools with @tool ───────────────────────────────────────
print("=" * 60)
print("LESSON 1: Creating tools with the @tool decorator")
print("=" * 60)

# The @tool decorator turns a Python function into a LangChain Tool
# KEY: The DOCSTRING is what the LLM reads to understand what the tool does!
# Make docstrings clear and descriptive!

@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.
    Use this for arithmetic, percentages, and basic math calculations.
    Examples: '2 + 2', '15% of 200', '(3 * 4) / 2 + 5', 'sqrt(144)'
    
    Args:
        expression: A mathematical expression as a string
    
    Returns:
        The calculated result as a string
    """
    try:
        # Replace common phrases with Python math
        expr = expression.lower()
        expr = expr.replace("sqrt", "math.sqrt")    # sqrt(x) → math.sqrt(x)
        expr = expr.replace("^", "**")              # 2^3 → 2**3
        
        # Handle "15% of 200" → "0.15 * 200"
        import re
        percent_match = re.match(r'(\d+\.?\d*)%\s*of\s*(\d+\.?\d*)', expr)
        if percent_match:
            pct, total = float(percent_match.group(1)), float(percent_match.group(2))
            return str(pct / 100 * total)
        
        result = eval(expr, {"math": math, "__builtins__": {}})  # Safe eval
        return f"{result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def get_current_datetime(timezone: str = "UTC") -> str:
    """
    Get the current date and time.
    Use this when the user asks about the current time, date, or day of the week.
    
    Args:
        timezone: Timezone name (e.g., 'UTC', 'US/Eastern'). Default is UTC.
    
    Returns:
        Current date and time as a formatted string
    """
    now = datetime.datetime.now()
    return f"Current datetime: {now.strftime('%A, %B %d, %Y at %H:%M:%S')} (local time)"


@tool
def search_knowledge_base(query: str, topic: Optional[str] = None) -> str:
    """
    Search the internal knowledge base for information.
    Use this to look up facts about Python, LangChain, or AI/ML topics.
    
    Args:
        query: The search query (what you're looking for)
        topic: Optional topic filter: 'python', 'langchain', 'ml', or None for all
    
    Returns:
        Relevant information from the knowledge base
    """
    # Simulated knowledge base (in real life, this calls your vector store!)
    kb = {
        "python": "Python is a high-level, interpreted programming language. Created by Guido van Rossum in 1991. Famous for readability and versatility.",
        "langchain": "LangChain is a framework for building LLM applications. Key components: LLMs, Prompts, Chains, Memory, Agents, Tools. Created by Harrison Chase in 2022.",
        "ml": "Machine Learning is a subset of AI. Key types: supervised (labeled data), unsupervised (clustering), reinforcement (rewards).",
        "rag": "RAG (Retrieval-Augmented Generation) combines vector search with LLM generation to answer questions about custom documents.",
        "transformers": "Transformers use self-attention to process sequences. Key innovation from Google Brain in 2017 paper 'Attention Is All You Need'.",
    }
    
    if topic and topic.lower() in kb:
        return kb[topic.lower()]
    
    # Simple keyword search
    query_lower = query.lower()
    for key, value in kb.items():
        if key in query_lower or query_lower in value.lower():
            return value
    
    return f"No information found for query: '{query}'"


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city.
    Use this when the user asks about weather conditions in a specific location.
    
    Args:
        city: Name of the city (e.g., 'London', 'New York', 'Tokyo')
    
    Returns:
        Current weather conditions as a string
    """
    # Simulated weather data (in real life, call OpenWeatherMap API)
    fake_weather = {
        "london": "Cloudy with light rain, 12°C (54°F), humidity 75%",
        "new york": "Sunny, 22°C (72°F), humidity 45%",
        "tokyo": "Clear skies, 18°C (64°F), humidity 60%",
        "paris": "Partly cloudy, 15°C (59°F), humidity 65%",
    }
    
    weather = fake_weather.get(city.lower(), f"Weather data not available for {city}")
    return f"Weather in {city}: {weather}"


# Let's see what each tool looks like
print(f"Tool: {calculate.name}")
print(f"Description: {calculate.description[:80]}...")
print(f"Args schema: {calculate.args}")

# You can call tools directly (without an agent)
print(f"\nDirect tool call: calculate('15% of 350')")
print(f"Result: {calculate.invoke({'expression': '15% of 350'})}")

print(f"\nDirect tool call: get_current_datetime()")
print(f"Result: {get_current_datetime.invoke({})}")


# ── LESSON 2: StructuredTool for Complex Inputs ───────────────────────────────
print("\n" + "=" * 60)
print("LESSON 2: StructuredTool for tools with multiple parameters")
print("=" * 60)

# When your tool has MULTIPLE required parameters, use StructuredTool
# with a Pydantic BaseModel for input validation

class SearchInput(BaseModel):
    """Input schema for the web search tool."""
    query: str = Field(description="The search query to look up")
    max_results: int = Field(default=3, description="Maximum number of results to return")
    site_filter: Optional[str] = Field(default=None, description="Restrict to a specific site (e.g., 'github.com')")

def web_search_function(query: str, max_results: int = 3, site_filter: Optional[str] = None) -> str:
    """Simulated web search function."""
    # In real life: use DuckDuckGo, Serper, Bing, etc.
    site_str = f" site:{site_filter}" if site_filter else ""
    return f"[Simulated] Top {max_results} results for '{query}{site_str}':\n" \
           f"1. Example result about {query}\n" \
           f"2. Another result about {query}\n" \
           f"3. Third result about {query}"

# Create StructuredTool from a function with Pydantic schema
web_search_tool = StructuredTool.from_function(
    func=web_search_function,
    name="web_search",
    description="Search the web for current information. Use for recent news, "
                "facts not in training data, or real-time information.",
    args_schema=SearchInput,        # Pydantic schema validates inputs
    return_direct=False,            # False = agent continues reasoning after result
                                    # True = agent returns this as final answer
)

print(f"StructuredTool: {web_search_tool.name}")
result = web_search_tool.invoke({
    "query": "LangChain latest version",
    "max_results": 2,
})
print(f"Result: {result[:100]}...")


# ── LESSON 3: Building a ReAct Agent ─────────────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 3: Building a ReAct Agent")
print("=" * 60)

print("""
ReAct = Reason + Act

The agent loop:
  Thought: I need to find the current time and then calculate 15% tip
  Action: get_current_datetime
  Action Input: {}
  Observation: Current datetime: Tuesday, March 5, 2024
  Thought: Now I need to calculate 15% of $75
  Action: calculate
  Action Input: {"expression": "15% of 75"}
  Observation: 11.25
  Thought: I have all the information
  Final Answer: The time is Tuesday, March 5, 2024. A 15% tip on $75 is $11.25.
""")

# All available tools for the agent
tools = [calculate, get_current_datetime, search_knowledge_base, get_weather]

# Use a pre-built ReAct prompt from LangChain hub
# hub.pull() downloads a community-shared prompt
# This prompt includes the ReAct format instructions
try:
    react_prompt = hub.pull("hwchase17/react")
    print("✅ Loaded ReAct prompt from hub")
except:
    # Fallback if no internet
    from langchain_core.prompts import PromptTemplate
    react_prompt = PromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")
    print("⚠️ Using fallback prompt (no internet)")

# Create the ReAct agent
agent = create_react_agent(
    llm=llm,            # The LLM that reasons and picks tools
    tools=tools,        # Available tools
    prompt=react_prompt # Prompt with ReAct format instructions
)

# AgentExecutor runs the agent loop with safety features
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,           # Print thought/action/observation loop
    max_iterations=5,       # Prevent infinite loops (safety limit)
    handle_parsing_errors=True,  # Don't crash on LLM formatting errors
    return_intermediate_steps=True,  # Return the reasoning steps
)

# Test the agent!
print("\n--- Agent Test 1: Math + DateTime ---")
result = agent_executor.invoke({
    "input": "What is today's date, and what is 22% of 450?"
})
print(f"Final Answer: {result['output']}")


# ── LESSON 4: Tool Calling (Modern Approach) ──────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 4: Tool Calling (bind_tools) — Modern Approach")
print("=" * 60)
print("""
Modern LLMs support "function calling" natively.
Instead of parsing "Action: tool_name" from text, the LLM returns
structured JSON specifying exactly which tool to call.

This is MUCH more reliable than ReAct string parsing.
""")

# Bind tools to the LLM directly
llm_with_tools = llm.bind_tools(tools)   # Tell the LLM about available tools

# The LLM can now return ToolCall objects instead of just text
response = llm_with_tools.invoke(
    "What is 42 * 7? Also, what's the weather like in Tokyo?"
)

print(f"Response type: {type(response)}")
print(f"Response content: {response.content}")   # Might be empty if tool_calls are made

if response.tool_calls:
    print(f"\nTool calls requested:")
    for tool_call in response.tool_calls:
        print(f"  Tool: {tool_call['name']}")          # Which tool to call
        print(f"  Args: {tool_call['args']}")           # With what arguments
        print(f"  ID:   {tool_call['id']}")             # For tracking
    
    # Execute the tool calls
    print("\nExecuting tools:")
    tool_map = {t.name: t for t in tools}   # Map name → tool
    
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        if tool_name in tool_map:
            result = tool_map[tool_name].invoke(tool_args)
            print(f"  {tool_name}({tool_args}) → {result}")


# ── LESSON 5: create_tool_calling_agent (Best Modern Agent) ──────────────────
print("\n" + "=" * 60)
print("LESSON 5: create_tool_calling_agent — Modern, Reliable Agent")
print("=" * 60)

from langchain.agents import create_tool_calling_agent

# This uses native tool calling instead of ReAct text parsing
# MUCH more reliable for production use!
modern_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to tools. "
               "Use tools when you need to calculate, check the time, or look up information. "
               "Always show your work."),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),   # Required for agents
])

# Create tool-calling agent (more reliable than ReAct)
modern_agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=modern_prompt,
)

modern_executor = AgentExecutor(
    agent=modern_agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True,
)

print("\n--- Modern Agent Test ---")
result = modern_executor.invoke({
    "input": "What is the weather in London, and can you also calculate 17% tip on $85.50?",
    "chat_history": [],  # Empty history (optional)
})
print(f"\nFinal Answer: {result['output']}")


# ── KEY TAKEAWAYS ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("KEY TAKEAWAYS FROM PROJECT 7:")
print("=" * 60)
print("""
1. @tool decorator turns any Python function into a LangChain tool
2. DOCSTRING is what the LLM reads — make it extremely clear!
3. StructuredTool + Pydantic = type-safe multi-parameter tools
4. ReAct agent = text-based reasoning loop (less reliable)
5. create_tool_calling_agent = uses native tool calling (MORE reliable)
6. AgentExecutor runs the loop safely with max_iterations limit
7. handle_parsing_errors=True prevents crashes from LLM mistakes
8. verbose=True shows the thinking process (great for debugging)
9. return_intermediate_steps=True gives you all the reasoning steps
10. llm.bind_tools(tools) — the modern way to give LLMs tools
""")
