"""
================================================================================
LANGGRAPH PROJECT 1: Your First Graph
================================================================================
WHAT IS LANGGRAPH?
  LangGraph is a framework for building STATEFUL, CYCLIC agent applications.
  
  LangChain = Linear pipelines (A → B → C)
  LangGraph = Graphs with loops (A → B → C → back to A if needed)
  
  KEY CONCEPTS:
  - State: A dict that flows through all nodes (shared memory)
  - Nodes: Python functions that READ and WRITE to state
  - Edges: Define which node runs NEXT (static or conditional)
  - Graph: The container that orchestrates everything

WHY LANGGRAPH?
  - LangChain chains can't loop back (you can't retry or iterate)
  - LangGraph can: "if answer is bad, try again" is just an edge
  - Perfect for: agents, multi-step workflows, iterative processes

STATE IS EVERYTHING:
  State is TypedDict (a typed dictionary)
  Every node receives the current state and returns an UPDATE to state
  Nodes don't replace state — they MERGE into it

================================================================================
"""

from typing import TypedDict, Annotated, List    # For state definition
import operator                                   # For Annotated reducers
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LangGraph imports
from langgraph.graph import StateGraph, END, START   # Core graph building blocks

from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama3-8b-8192", temperature=0)


# ── LESSON 1: Define State ────────────────────────────────────────────────────
print("=" * 60)
print("LANGGRAPH P1: Your First Graph")
print("=" * 60)

# State is a TypedDict — it defines ALL the data your graph will use
# Think of it as the "shared whiteboard" all nodes can read and write

class SimpleState(TypedDict):
    """
    State for our simple graph.
    Every field here can be read and updated by any node.
    """
    user_input: str         # The original user question
    processed_input: str    # After preprocessing
    llm_response: str       # LLM's answer
    final_output: str       # Formatted final output


# ── LESSON 2: Define Nodes ────────────────────────────────────────────────────
# Each node is a FUNCTION:
#   Input:  current state (dict)
#   Output: dict with keys to UPDATE in state (partial update!)

def preprocess_node(state: SimpleState) -> dict:
    """
    Node 1: Clean and prepare the user input.
    Reads: state["user_input"]
    Writes: processed_input
    """
    raw = state["user_input"]
    
    # Clean the input
    processed = raw.strip()                 # Remove whitespace
    processed = processed.rstrip("?") + "?"  # Ensure ends with ?
    processed = processed.capitalize()      # Capitalize first letter
    
    print(f"  [Preprocess] '{raw}' → '{processed}'")
    
    # Return only the keys this node is CHANGING
    # LangGraph MERGES this into the existing state
    return {"processed_input": processed}


def llm_node(state: SimpleState) -> dict:
    """
    Node 2: Call the LLM with the processed input.
    Reads: state["processed_input"]
    Writes: llm_response
    """
    question = state["processed_input"]
    
    # Call the LLM
    response = llm.invoke(f"Answer concisely: {question}")
    
    print(f"  [LLM] Answering: {question[:40]}...")
    
    return {"llm_response": response.content}


def format_output_node(state: SimpleState) -> dict:
    """
    Node 3: Format the final output nicely.
    Reads: state["user_input"], state["llm_response"]
    Writes: final_output
    """
    question = state["user_input"]
    answer = state["llm_response"]
    
    formatted = f"Q: {question}\nA: {answer}\n{'─' * 40}"
    
    return {"final_output": formatted}


# ── LESSON 3: Build the Graph ─────────────────────────────────────────────────
print("Building graph...")

# StateGraph(StateType) — creates a new graph with our state definition
graph_builder = StateGraph(SimpleState)

# Add nodes — give each function a name in the graph
graph_builder.add_node("preprocess", preprocess_node)    # Name → function
graph_builder.add_node("llm_call", llm_node)
graph_builder.add_node("format_output", format_output_node)

# Add edges — define the flow
graph_builder.add_edge(START, "preprocess")         # START is the entry point
graph_builder.add_edge("preprocess", "llm_call")    # After preprocess → llm_call
graph_builder.add_edge("llm_call", "format_output") # After llm_call → format
graph_builder.add_edge("format_output", END)        # After format → END (done)

# Compile: turns the builder into a runnable graph
graph = graph_builder.compile()

# ── LESSON 4: Run the Graph ───────────────────────────────────────────────────
print("Running graph...\n")

initial_state = {
    "user_input": "what is python",
    "processed_input": "",   # Will be filled by preprocess node
    "llm_response": "",
    "final_output": "",
}

# .invoke() runs the full graph and returns final state
final_state = graph.invoke(initial_state)

print(f"\nFinal State:")
print(f"  user_input: {final_state['user_input']}")
print(f"  processed_input: {final_state['processed_input']}")
print(f"  llm_response: {final_state['llm_response'][:80]}...")
print(f"\n{final_state['final_output']}")

# 💡 .stream() also works — yields state after each node!
print("\nStreaming (state after each node):")
for event in graph.stream({"user_input": "what is langchain", "processed_input": "", "llm_response": "", "final_output": ""}):
    # event is a dict: {node_name: {state_updates}}
    for node_name, state_update in event.items():
        print(f"  After [{node_name}]: {list(state_update.keys())}")


"""
================================================================================
LANGGRAPH PROJECT 2: Conditional Edges — Routing
================================================================================
WHAT YOU LEARN:
  - add_conditional_edges: route to different nodes based on state
  - Router functions: decide where to go next
  - Cycles: graphs that loop back (the key advantage of LangGraph)
  - The "__end__" sentinel vs END import
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P2: Conditional Edges")
print("=" * 60)

class RouterState(TypedDict):
    """State for routing example."""
    question: str           # User's question
    category: str           # Classified category
    answer: str             # Final answer
    attempts: int           # How many times we've tried


def classify_node(state: RouterState) -> dict:
    """Classify the question into a category."""
    question = state["question"].lower()
    
    if any(w in question for w in ["calculate", "math", "compute", "solve", "+"]):
        category = "math"
    elif any(w in question for w in ["code", "python", "function", "program"]):
        category = "coding"
    elif any(w in question for w in ["who", "when", "history", "year"]):
        category = "general"
    else:
        category = "unknown"
    
    print(f"  [Classify] '{state['question'][:30]}' → category: {category}")
    return {"category": category, "attempts": state.get("attempts", 0) + 1}


def math_expert_node(state: RouterState) -> dict:
    """Handle math questions."""
    answer = llm.invoke(f"You are a math expert. Solve: {state['question']}")
    print(f"  [Math Expert] Answering...")
    return {"answer": f"[MATH] {answer.content}"}


def coding_expert_node(state: RouterState) -> dict:
    """Handle coding questions."""
    answer = llm.invoke(f"You are a coding expert. Answer: {state['question']}")
    print(f"  [Code Expert] Answering...")
    return {"answer": f"[CODE] {answer.content}"}


def general_expert_node(state: RouterState) -> dict:
    """Handle general questions."""
    answer = llm.invoke(f"Answer this question: {state['question']}")
    print(f"  [General] Answering...")
    return {"answer": f"[GENERAL] {answer.content}"}


def fallback_node(state: RouterState) -> dict:
    """Handle unknown category — rephrase and try again."""
    print(f"  [Fallback] Unknown category, rephrasing...")
    rephrased = llm.invoke(
        f"Rephrase this as a clear question: {state['question']}"
    )
    return {"question": rephrased.content}


# ROUTER FUNCTION — returns the NAME of the next node
def route_by_category(state: RouterState) -> str:
    """
    Conditional edge function.
    Returns the NAME of the next node to visit.
    Must return a valid node name or END.
    """
    category = state["category"]
    attempts = state.get("attempts", 0)
    
    # Safety valve: prevent infinite loops
    if attempts >= 3:
        print(f"  [Router] Max attempts reached, going to general")
        return "general_expert"
    
    # Route based on category
    if category == "math":
        return "math_expert"       # Go to math expert node
    elif category == "coding":
        return "coding_expert"     # Go to coding expert node
    elif category == "general":
        return "general_expert"    # Go to general expert node
    else:
        return "fallback"          # Unknown → rephrase and try again


# Build the graph
router_builder = StateGraph(RouterState)

# Add all nodes
router_builder.add_node("classify", classify_node)
router_builder.add_node("math_expert", math_expert_node)
router_builder.add_node("coding_expert", coding_expert_node)
router_builder.add_node("general_expert", general_expert_node)
router_builder.add_node("fallback", fallback_node)

# Entry point
router_builder.add_edge(START, "classify")

# CONDITIONAL EDGE from classify — calls route_by_category() to decide
router_builder.add_conditional_edges(
    "classify",           # Source node
    route_by_category,    # Function that returns next node name
    {                     # Map: return value → node name (optional but explicit)
        "math_expert":    "math_expert",
        "coding_expert":  "coding_expert",
        "general_expert": "general_expert",
        "fallback":       "fallback",
    }
)

# After fallback → re-classify (THE LOOP!)
router_builder.add_edge("fallback", "classify")

# All expert nodes → END
router_builder.add_edge("math_expert", END)
router_builder.add_edge("coding_expert", END)
router_builder.add_edge("general_expert", END)

router_graph = router_builder.compile()

# Test routing
test_questions = [
    "Calculate 15% of 200",
    "Write a Python function to reverse a list",
    "When was Python created?",
]

for q in test_questions:
    print(f"\nQ: {q}")
    result = router_graph.invoke({
        "question": q,
        "category": "",
        "answer": "",
        "attempts": 0,
    })
    print(f"A: {result['answer'][:100]}...")


"""
================================================================================
LANGGRAPH PROJECT 3: Memory & Persistent State
================================================================================
WHAT YOU LEARN:
  - Checkpointers: save/load state automatically
  - MemorySaver: in-memory persistence (for development)
  - Thread IDs: separate conversation sessions
  - State continuity across multiple invocations
  - Resuming a graph from saved state
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P3: Memory & Persistent State")
print("=" * 60)

from langgraph.checkpoint.memory import MemorySaver

# For persistent storage (use in production):
# from langgraph.checkpoint.sqlite import SqliteSaver  # SQLite file
# from langgraph.checkpoint.postgres import PostgresSaver  # PostgreSQL

# State with message history
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]   # SPECIAL: operator.add means APPEND
    # Without Annotated[List, operator.add], new messages would REPLACE old ones
    # With it, each update APPENDS to the list — perfect for chat history
    user_name: str
    turn_count: int


def chat_node(state: ChatState) -> dict:
    """Chat node that maintains conversation history."""
    
    # The full message history is in state["messages"]
    messages = state["messages"]
    
    print(f"  [Chat] Turn {state.get('turn_count', 0) + 1} | History: {len(messages)} messages")
    
    # Call LLM with full history (LangGraph gives us memory for free!)
    response = llm.invoke(messages)
    
    return {
        "messages": [response],              # APPENDED to history (not replaced!)
        "turn_count": state.get("turn_count", 0) + 1,
    }


def set_name_node(state: ChatState) -> dict:
    """Extract user name from first message."""
    first_msg = state["messages"][0].content if state["messages"] else ""
    
    # Try to find a name
    if "name is" in first_msg.lower():
        parts = first_msg.lower().split("name is")
        if len(parts) > 1:
            name = parts[1].strip().split()[0].capitalize()
            return {"user_name": name}
    
    return {"user_name": "Unknown"}


# Build chat graph with memory
memory_builder = StateGraph(ChatState)
memory_builder.add_node("extract_name", set_name_node)
memory_builder.add_node("chat", chat_node)

memory_builder.add_edge(START, "extract_name")
memory_builder.add_edge("extract_name", "chat")
memory_builder.add_edge("chat", END)

# MemorySaver stores state after each step — KEY for persistence!
checkpointer = MemorySaver()

# Pass checkpointer when compiling
memory_graph = memory_builder.compile(checkpointer=checkpointer)

# Thread ID identifies a specific conversation
# Same thread_id = same conversation (state is loaded automatically!)
config_alice = {"configurable": {"thread_id": "alice_session_1"}}

print("Alice's Conversation:")

# Turn 1 — starts new conversation
result = memory_graph.invoke(
    {"messages": [HumanMessage("Hi! My name is Alice.")], "user_name": "", "turn_count": 0},
    config=config_alice    # Must pass config with thread_id!
)
print(f"  Alice T1: {result['messages'][-1].content[:80]}")

# Turn 2 — state is AUTOMATICALLY loaded from checkpointer!
result = memory_graph.invoke(
    {"messages": [HumanMessage("What is my name?")]},   # Note: no need to send full history
    config=config_alice    # Same thread_id = same conversation
)
print(f"  Alice T2: {result['messages'][-1].content[:80]}")   # Should remember Alice!

# Turn 3
result = memory_graph.invoke(
    {"messages": [HumanMessage("How many messages have we exchanged?")]},
    config=config_alice
)
print(f"  Alice T3: {result['messages'][-1].content[:80]}")

# Get the current state without invoking
saved_state = memory_graph.get_state(config_alice)
print(f"\nSaved state turn count: {saved_state.values.get('turn_count')}")
print(f"Total messages in history: {len(saved_state.values.get('messages', []))}")


"""
================================================================================
LANGGRAPH PROJECT 4: Human-in-the-Loop
================================================================================
WHAT YOU LEARN:
  - interrupt_before: Pause graph before a node for human approval
  - interrupt_after: Pause graph after a node
  - Inspecting pending state
  - Resuming with or without modifications
  - Adding human feedback to state

USE CASES:
  - "Before spending money, confirm with user"
  - "Before sending email, let human review"
  - "After generating code, run tests, then ask human to approve"
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P4: Human-in-the-Loop")
print("=" * 60)

from langgraph.types import interrupt, Command

class ApprovalState(TypedDict):
    """State for approval workflow."""
    task: str               # What we're trying to do
    plan: str               # AI-generated plan
    human_approved: bool    # Did human approve?
    human_feedback: str     # Optional feedback from human
    result: str             # Final result after approval


def plan_node(state: ApprovalState) -> dict:
    """Generate a plan for the task."""
    task = state["task"]
    plan = f"PLAN for '{task}':\n1. First step\n2. Second step\n3. Execute and verify"
    print(f"  [Planner] Generated plan for: {task[:40]}")
    return {"plan": plan}


def human_approval_node(state: ApprovalState) -> dict:
    """
    This is where human-in-the-loop happens.
    The graph PAUSES here and waits for human input.
    """
    # interrupt() PAUSES the graph and returns control to the caller
    # The caller can then inspect state, modify it, and resume
    
    print(f"  [HumanApproval] ⏸️  PAUSED — waiting for human approval")
    print(f"  Plan to approve:\n{state['plan']}")
    
    # interrupt() can pass information to the human
    # This information is available in the interrupt exception
    human_response = interrupt({
        "question": "Do you approve this plan?",
        "plan": state["plan"],
        "options": ["approve", "reject", "modify"],
    })
    
    # When graph resumes, human_response contains what was passed to .invoke()
    approved = human_response.get("approved", False)
    feedback = human_response.get("feedback", "")
    
    return {
        "human_approved": approved,
        "human_feedback": feedback,
    }


def execute_node(state: ApprovalState) -> dict:
    """Execute the plan (only if approved)."""
    if state["human_approved"]:
        result = f"✅ Executed: {state['plan']}"
        print(f"  [Execute] Plan approved and executed!")
    else:
        result = f"❌ Rejected: {state.get('human_feedback', 'No reason given')}"
        print(f"  [Execute] Plan rejected.")
    return {"result": result}


def route_after_approval(state: ApprovalState) -> str:
    """Route: if approved → execute, else → end."""
    return "execute" if state["human_approved"] else END


# Build human-in-loop graph
hitl_builder = StateGraph(ApprovalState)
hitl_builder.add_node("plan", plan_node)
hitl_builder.add_node("human_approval", human_approval_node)
hitl_builder.add_node("execute", execute_node)

hitl_builder.add_edge(START, "plan")
hitl_builder.add_edge("plan", "human_approval")
hitl_builder.add_conditional_edges("human_approval", route_after_approval, {"execute": "execute", END: END})
hitl_builder.add_edge("execute", END)

# MUST use checkpointer for human-in-the-loop to work!
hitl_checkpointer = MemorySaver()
hitl_graph = hitl_builder.compile(
    checkpointer=hitl_checkpointer,
    interrupt_before=["human_approval"],   # Pause BEFORE this node
)

task_config = {"configurable": {"thread_id": "task_001"}}

print("\n--- Running until interrupt ---")
initial_state = {
    "task": "Send marketing email to all users",
    "plan": "",
    "human_approved": False,
    "human_feedback": "",
    "result": "",
}

# First .invoke() runs until the interrupt
try:
    result = hitl_graph.invoke(initial_state, config=task_config)
except Exception as e:
    # Interrupt raises an exception — this is expected!
    pass

# Inspect the paused state
paused_state = hitl_graph.get_state(task_config)
print(f"\n⏸️  Graph paused at: {paused_state.next}")
print(f"Pending approval for plan: {paused_state.values.get('plan', '')[:80]}")

# Simulate human APPROVING the plan
print("\n--- Human approves ---")
result = hitl_graph.invoke(
    Command(resume={"approved": True, "feedback": "Looks good, proceed!"}),
    config=task_config
)
print(f"Final result: {result.get('result', 'N/A')[:100]}")


print("\n" + "=" * 60)
print("KEY TAKEAWAYS FROM LANGGRAPH P1-P4:")
print("=" * 60)
print("""
P1 - First Graph:
  StateGraph(State) → add_node() → add_edge() → compile() → invoke()
  Nodes return PARTIAL state updates (only changed keys)
  
P2 - Conditional Edges:
  add_conditional_edges(source, router_fn, {return_val: node_name})
  Router function returns a node name as a string
  Loops are just edges that go back to earlier nodes
  
P3 - Memory:
  MemorySaver() as checkpointer → compile(checkpointer=...)
  config={"configurable": {"thread_id": "..."}} identifies session
  Annotated[List, operator.add] → APPEND mode for lists
  
P4 - Human-in-the-Loop:
  interrupt() pauses the graph and returns control to caller
  compile(interrupt_before=["node_name"]) pauses BEFORE that node
  Resume with Command(resume={...}) or just .invoke(data, config)
""")
