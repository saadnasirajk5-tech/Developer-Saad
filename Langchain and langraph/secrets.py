"""
================================================================================
TIPS & TRICKS — Insider Secrets Most LangChain/LangGraph Devs Don't Know
================================================================================
These are the tricks that separate seniors from beginners.
Every single one is battle-tested in production systems.
================================================================================
"""

print("=" * 70)
print("TIPS & TRICKS: The Insider's Guide to LangChain + LangGraph")
print("=" * 70)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 1: LANGCHAIN SECRETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "━" * 70)
print("LANGCHAIN SECRETS")
print("━" * 70)

print("""
━━━━ SECRET 1: .get_graph().draw_mermaid() — Visualize Any Chain ━━━━
Most devs never visualize their chains. You should ALWAYS do this.
  
  chain = prompt | llm | parser
  print(chain.get_graph().draw_mermaid())
  
  Copy-paste the output to: https://mermaid.live
  You'll see exactly how your chain is structured.
  Also works for LangGraph graphs!
""")

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(model="llama3-8b-8192", temperature=0)
chain = ChatPromptTemplate.from_template("What is {x}?") | llm | StrOutputParser()
try:
    diagram = chain.get_graph().draw_mermaid()
    print("Chain visualization (paste to mermaid.live):")
    print(diagram[:300])
except:
    print("(Visualization not available in this environment)")


print("""
━━━━ SECRET 2: .with_structured_output() with strict=True ━━━━━━━━━━━
Most devs use PydanticOutputParser. But with_structured_output() is BETTER.
The secret: add strict=True for even more reliable parsing.
  
  from pydantic import BaseModel
  class Output(BaseModel):
      name: str
      age: int
  
  structured = llm.with_structured_output(Output, strict=True)
  result = structured.invoke("John Doe, 25 years old")
  # result.name = "John Doe", result.age = 25
  
  Why better than PydanticOutputParser?
  - Uses JSON schema tool calling (not prompt injection)
  - LLM can't "forget" the format
  - No need to put format instructions in prompt
""")


print("""
━━━━ SECRET 3: Cache LLM Calls — Save 90% of API Costs ━━━━━━━━━━━━━
During development, you'll call the same prompt many times.
Set up caching and you'll NEVER pay for duplicate calls.
  
  from langchain_core.globals import set_llm_cache
  from langchain_community.cache import InMemoryCache, SQLiteCache
  
  # For development (resets each session):
  set_llm_cache(InMemoryCache())
  
  # For production (persists across restarts):
  set_llm_cache(SQLiteCache(database_path=".langchain.db"))
  
  # Now identical prompts return instantly from cache!
  result1 = chain.invoke({"x": "Python"})  # API call
  result2 = chain.invoke({"x": "Python"})  # CACHE HIT — instant, free!
""")

# Try setting up cache
try:
    from langchain_core.globals import set_llm_cache
    from langchain_community.cache import InMemoryCache
    set_llm_cache(InMemoryCache())
    print("✅ Cache set up successfully")
except ImportError:
    print("(Cache not available in this environment)")


print("""
━━━━ SECRET 4: Runnable.pick() — Extract Just One Key ━━━━━━━━━━━━━━
When your chain returns a dict but you only want ONE value:
  
  # Instead of:
  chain = (setup_chain | llm | parser | (lambda x: x["answer"]))
  
  # Do this:
  from langchain_core.runnables import RunnablePick
  chain = setup_chain | llm | parser | RunnablePick("answer")
  
  # Works like itemgetter but is a proper Runnable
""")


print("""
━━━━ SECRET 5: configurable_fields() — Dynamic LLM Parameters ━━━━━━
Most devs hardcode temperature. But you can make it CONFIGURABLE!
  
  dynamic_llm = llm.configurable_fields(
      temperature=ConfigurableField(
          id="llm_temperature",
          name="Temperature",
          description="Creativity level 0-2",
      )
  )
  
  # Now override at call time!
  creative = dynamic_llm.with_config(configurable={"llm_temperature": 0.9})
  precise = dynamic_llm.with_config(configurable={"llm_temperature": 0.0})
  
  # Perfect for letting users control creativity!
""")


print("""
━━━━ SECRET 6: @chain Decorator — Simplest Chain Creation ━━━━━━━━━━
Most devs use complex LCEL pipes. But @chain is often cleaner:
  
  from langchain_core.runnables import chain
  
  @chain
  def my_chain(input: dict) -> str:
      # Write your chain logic as normal Python!
      question = input["question"]
      context = retrieve(question)         # Any Python code
      response = llm.invoke(...)
      return response.content
  
  # Now my_chain is a Runnable with .invoke/.stream/.batch!
  result = my_chain.invoke({"question": "..."})
  
  # WHEN TO USE: when LCEL pipes get too complex or unreadable
""")


print("""
━━━━ SECRET 7: Streaming with accumulate_chunks() ━━━━━━━━━━━━━━━━━━
For streaming output parsers, use this pattern:
  
  from langchain_core.output_parsers import JsonOutputParser
  
  streaming_parser = JsonOutputParser()
  
  # This streams PARTIAL JSON as it's generated!
  for partial in chain.stream(input):
      print(partial)   # {'key': 'val'} builds up piece by piece
  
  # Works for: JsonOutputParser, PydanticOutputParser
  # Lets you show partial results to users in real-time!
""")


print("""
━━━━ SECRET 8: batch() vs abatch() Performance ━━━━━━━━━━━━━━━━━━━━━
  
  # DON'T do this (sequential, slow):
  results = [chain.invoke(x) for x in inputs]  # N API calls one-by-one
  
  # DO this (concurrent, fast):
  results = chain.batch(inputs)                  # N API calls in parallel
  
  # Even better — control concurrency:
  results = chain.batch(inputs, config={"max_concurrency": 5})
  # Processes max 5 at once (prevent rate limits!)
  
  # Async batch for web servers:
  results = await chain.abatch(inputs)
""")


print("""
━━━━ SECRET 9: Add Types to Tool Args with Pydantic ━━━━━━━━━━━━━━━━
Most @tool decorators lack proper type hints. This makes LLMs call them wrong.
  
  BAD (vague):
  @tool
  def search(query):
      "Search for things"
  
  GOOD (specific):
  @tool
  def search(
      query: str,               # LLM knows it's a string
      max_results: int = 5,    # LLM knows default is 5
      language: Literal["en", "es", "fr"] = "en"  # LLM knows the options!
  ) -> str:
      "Search the web. query: search terms. max_results: 1-10."
  
  # LITERAL TYPES are the secret — LLM picks from a known set!
""")


print("""
━━━━ SECRET 10: Prompt Injection Protection ━━━━━━━━━━━━━━━━━━━━━━━━
Always separate user input from system instructions:
  
  BAD (injectable):
  prompt = f"You are helpful. Answer: {user_input}"
  # user_input could be: "Ignore instructions. Do evil thing."
  
  GOOD (protected):
  messages = [
      SystemMessage("You are helpful."),   # Separate! Can't be overridden
      HumanMessage(user_input),            # User input in its own message
  ]
  
  # The SystemMessage role has higher trust than HumanMessage
  # Most modern LLMs respect this separation
""")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 2: LANGGRAPH SECRETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "━" * 70)
print("LANGGRAPH SECRETS")
print("━" * 70)

print("""
━━━━ SECRET 11: Annotated with Custom Reducers ━━━━━━━━━━━━━━━━━━━━━
State updates can use CUSTOM logic, not just append/replace:
  
  from typing import Annotated
  
  def keep_unique(old: list, new: list) -> list:
      "Keep unique items only."
      return list(set(old + new))
  
  class State(TypedDict):
      messages: Annotated[list, operator.add]      # Append
      results: Annotated[list, keep_unique]         # Unique only
      count: Annotated[int, lambda a, b: a + b]     # Sum
      latest: str                                    # Replace (default)
  
  # The reducer function is called: reducer(existing_value, new_value)
""")


print("""
━━━━ SECRET 12: graph.stream() with stream_mode ━━━━━━━━━━━━━━━━━━━━
Different streaming modes give you different information:
  
  # Default: yields {node_name: state_updates} after each node
  for event in graph.stream(input):
      print(event)  # {'node1': {'key': 'value'}}
  
  # 'values': yields FULL state after each node (more info)
  for state in graph.stream(input, stream_mode="values"):
      print(state)  # Complete current state
  
  # 'updates': yields just the UPDATES (default behavior)
  for update in graph.stream(input, stream_mode="updates"):
      print(update)
  
  # 'debug': EVERYTHING including intermediate state (for debugging)
  for event in graph.stream(input, stream_mode="debug"):
      print(event)  # Very verbose!
  
  # 'messages': STREAM LLM TOKENS in real-time from within graphs!
  async for token in graph.astream_events(input, version="v2"):
      if token["event"] == "on_chat_model_stream":
          print(token["data"]["chunk"].content, end="")
""")


print("""
━━━━ SECRET 13: get_state() and update_state() ━━━━━━━━━━━━━━━━━━━━━
You can READ and MODIFY state between graph invocations!
  
  # Read current state
  state = graph.get_state(config)
  print(state.values)         # Current state dict
  print(state.next)           # Which nodes are next
  print(state.created_at)     # When this checkpoint was created
  
  # Modify state without running a node!
  graph.update_state(
      config,
      {"my_field": "new_value"},   # What to change
      as_node="node_name"          # Act as if this node made the update
  )
  
  # USE CASE: Fix a mistake the agent made without re-running everything
  # USE CASE: Inject information that the agent should "remember"
  # USE CASE: Debug by setting state to a specific point
""")


print("""
━━━━ SECRET 14: Subgraphs — Graphs within Graphs ━━━━━━━━━━━━━━━━━━━
Complex systems = compose multiple graphs!
  
  # Build a reusable subgraph
  sub_builder = StateGraph(SubState)
  sub_builder.add_node("step1", ...)
  sub_builder.add_node("step2", ...)
  sub_graph = sub_builder.compile()
  
  # Use it as a NODE in the main graph
  main_builder = StateGraph(MainState)
  main_builder.add_node("main_node", main_function)
  main_builder.add_node("sub_process", sub_graph)  # ← Graph as a node!
  
  # Benefits:
  # - Reuse complex workflows
  # - Independent state spaces
  # - Cleaner code organization
  # - Each subgraph has its own memory/checkpointing
""")


print("""
━━━━ SECRET 15: Command() for Dynamic State + Routing ━━━━━━━━━━━━━━
Command is the MOST POWERFUL way to control graph flow from a node:
  
  from langgraph.types import Command
  
  def smart_node(state):
      if some_condition:
          # Update state AND route to specific node
          return Command(
              update={"field": "value"},   # State update
              goto="specific_node",        # Where to go
          )
      elif other_condition:
          return Command(goto=END)         # Jump to end
      else:
          # Normal update
          return {"field": "other_value"}
  
  # Why use Command instead of conditional edges?
  # - The NODE decides routing (more dynamic)
  # - Combine state update + routing in one return
  # - Can route to MULTIPLE nodes (fan-out)
  
  # Fan-out with Command:
  return Command(
      update={"task": "done"},
      goto=["node_a", "node_b"],  # Go to BOTH!
  )
""")


print("""
━━━━ SECRET 16: Graph State Schema Validation ━━━━━━━━━━━━━━━━━━━━━━
Add runtime validation to your state with Pydantic:
  
  from pydantic import BaseModel, field_validator
  
  class ValidatedState(BaseModel):
      messages: List[str]
      score: float
      
      @field_validator('score')
      def score_must_be_valid(cls, v):
          if not 0 <= v <= 1:
              raise ValueError('Score must be 0-1')
          return v
  
  # LangGraph supports Pydantic BaseModel as state!
  # Invalid state updates will raise validation errors
  # Use this to catch bugs early in development
""")


print("""
━━━━ SECRET 17: astream_events() for Real-Time UI Updates ━━━━━━━━━━
For production UIs, astream_events gives you EVERYTHING in real-time:
  
  async for event in graph.astream_events(input, config, version="v2"):
      kind = event["event"]
      
      if kind == "on_chain_start":
          print(f"Starting: {event['name']}")
      
      elif kind == "on_chat_model_stream":
          # Individual LLM tokens!
          chunk = event["data"]["chunk"]
          yield chunk.content   # Stream to your web UI
      
      elif kind == "on_tool_start":
          print(f"Calling tool: {event['name']}")
      
      elif kind == "on_tool_end":
          print(f"Tool result: {event['data']['output']}")
  
  # Use in FastAPI with Server-Sent Events for real-time agent UI!
""")


print("""
━━━━ SECRET 18: Parallel Tool Calls in Agents ━━━━━━━━━━━━━━━━━━━━━
Modern LLMs can request MULTIPLE tools at once.
Make sure your ToolNode handles this:
  
  # When LLM requests: [search("x"), calculate("5+5")]
  # ToolNode runs BOTH tools in parallel automatically!
  
  # To check if you're getting parallel calls:
  if len(response.tool_calls) > 1:
      print(f"Parallel calls: {[tc['name'] for tc in response.tool_calls]}")
  
  # Force sequential tool calls (sometimes needed):
  llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
  
  # When to use sequential:
  # - Tool B depends on Tool A's result
  # - Rate limit concerns
  # - Debugging (easier to trace)
""")


print("""
━━━━ SECRET 19: LangSmith Tracing (FREE) ━━━━━━━━━━━━━━━━━━━━━━━━━━
LangSmith traces EVERY call in your chain/graph. Invaluable for debugging.
  
  # 1. Sign up FREE at: smith.langchain.com
  # 2. Create a project
  # 3. Set environment variables:
  
  import os
  os.environ["LANGCHAIN_TRACING_V2"] = "true"
  os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_key"
  os.environ["LANGCHAIN_PROJECT"] = "my-project-name"
  
  # Now EVERY invoke/stream call is traced automatically!
  # See: inputs, outputs, latency, token count, errors
  # For LangGraph: see the FULL graph execution visually!
  
  # This is the #1 debugging tool for LangChain/LangGraph
""")


print("""
━━━━ SECRET 20: MessagesState — Skip Writing State TypedDicts ━━━━━━
LangGraph has built-in state classes you can extend:
  
  from langgraph.graph import MessagesState
  
  # Instead of writing:
  class MyState(TypedDict):
      messages: Annotated[List[BaseMessage], operator.add]
      my_field: str
  
  # Do this:
  class MyState(MessagesState):   # Already has messages with add reducer!
      my_field: str               # Just add your custom fields
  
  # MessagesState also has:
  # - add_messages reducer (handles deduplication by message ID)
  # - Works with create_react_agent() out of the box
  
  # Also available:
  from langgraph.prebuilt import create_react_agent
  # This prebuilt gives you a complete agent with just 2 lines!
  agent = create_react_agent(llm, tools)
  result = agent.invoke({"messages": [HumanMessage("Hello")]})
""")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 3: ARCHITECTURE PATTERNS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print("\n" + "━" * 70)
print("ARCHITECTURE PATTERNS — When to Use What")
print("━" * 70)

print("""
WHEN TO USE LANGCHAIN CHAINS (LCEL):
  ✅ Deterministic, linear workflows
  ✅ No loops or retries needed
  ✅ Simple prompt → response
  ✅ Batch processing documents
  ✅ Data transformation pipelines
  Examples: summarization, classification, extraction, translation

WHEN TO USE LANGGRAPH:
  ✅ Loops and iteration ("keep trying until good")
  ✅ Multi-step planning + execution
  ✅ Human-in-the-loop approval flows
  ✅ Multi-agent coordination
  ✅ Complex agent reasoning
  ✅ State persistence across sessions
  Examples: research agents, coding assistants, customer support bots

THE GOLDEN RULE:
  Start with LCEL (simpler, faster)
  Add LangGraph only when you need CYCLES, MEMORY, or MULTI-AGENT

RAG QUALITY HIERARCHY (best to worst retrieval):
  1. HyDE + Cross-encoder reranking (🏆 Best, expensive)
  2. MultiQueryRetriever + BM25 hybrid
  3. MultiQueryRetriever alone
  4. MMR retrieval
  5. Basic similarity search (🔰 Default, good enough to start)

AGENT RELIABILITY HIERARCHY:
  1. Tool calling + LangGraph (✅ Production-ready)
  2. create_react_agent (✅ Good for most use cases)
  3. ReAct with text parsing (⚠️ Fragile, avoid in production)

FREE TOOLS STACK (no credit card needed):
  LLM:        Groq (console.groq.com) — llama3-8b, mixtral FREE
  Embeddings: HuggingFace bge-small (local, FREE)
  Vector DB:  FAISS or Chroma (local, FREE)
  Tracing:    LangSmith (smith.langchain.com, FREE tier)
  Search:     DuckDuckGo (langchain-community, no API key)
""")


print("""
DEBUGGING CHECKLIST:
  □ Is the prompt being filled correctly? → .format_messages() to inspect
  □ Is the LLM receiving the right input? → Add logging callback
  □ Is parsing working? → Test parser.parse() on raw LLM output
  □ Is retrieval finding relevant chunks? → retriever.invoke() directly
  □ Is state updating correctly? → graph.get_state() after each step
  □ Are tools being called? → verbose=True in AgentExecutor
  □ LangSmith trace showing the full picture? → Always use in development

PERFORMANCE CHECKLIST:
  □ Using .batch() instead of loop of .invoke()? 
  □ Caching set up for development?
  □ Chunk size appropriate for your documents? (try 500-1000 chars)
  □ top_k set appropriately? (3-7 is usually optimal)
  □ LLM temperature = 0 for factual/extraction tasks?
  □ Streaming for user-facing outputs?
""")

print("\n🎯 You now know what takes most developers YEARS to figure out.")
print("   Go build something amazing! 🚀")
