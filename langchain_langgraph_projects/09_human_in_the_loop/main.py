import os
from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
# We need a checkpointer to save the graph's memory state!
from langgraph.checkpoint.memory import MemorySaver 

load_dotenv(dotenv_path='../.env')

class HITLState(TypedDict):
    task: str
    email_draft: str
    is_approved: bool

def drafter_node(state: HITLState):
    print("--- 🪶 Running Drafter Node ---")
    # Simulating LLM action
    task = state["task"]
    draft = f"Subject: Proposal\n\nDear Boss,\n\nI am writing regarding: {task}. Please let me know your thoughts.\n\nBest,\nYour AI Drafter"
    return {"email_draft": draft}

def review_node(state: HITLState):
    print("--- 🛑 Review Node (Paused for Human) ---")
    # This node actually barely does anything because the graph pauses BEFORE it!
    # By the time it runs, the human has injected the 'is_approved' state.
    if state.get("is_approved", False):
        print("Human approval confirmed within graph state.")
    else:
        print("Human REJECTED the email.")
    return state # No changes needed, just a passthrough for logic

def sender_node(state: HITLState):
    print("--- ✉️ Running Sender Node ---")
    print(f"Sending email... \n{state['email_draft']}\n[Email Sent Successfully!]")
    return state

def routing_logic(state: HITLState):
    if state.get("is_approved"):
        return "sender"
    else:
        # If user rejects, we skip sending and just end.
        return "end"

def main():
    print("🚀 Starting Human-in-the-loop (HITL) Workflow")

    # 1. Setup MemorySaver. 
    # State Graphs with interrupts REQUIRE memory because they literally stop 
    # execution and need to 'remember' where they were when resumed.
    checkpointer = MemorySaver()

    builder = StateGraph(HITLState)

    builder.add_node("drafter", drafter_node)
    builder.add_node("review", review_node)
    builder.add_node("sender", sender_node)

    builder.add_edge(START, "drafter")
    builder.add_edge("drafter", "review")
    builder.add_conditional_edges(
        "review",
        routing_logic,
        {"sender": "sender", "end": END}
    )
    builder.add_edge("sender", END)

    # 2. Compile with an interrupt flag!
    # We tell LangGraph: "Pause BEFORE you execute the 'review' node."
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["review"]
    )

    # 3. First execution run (will hit the pause)
    # We use a thread_id so the checkpointer knows which memory to look up.
    config = {"configurable": {"thread_id": "session_1"}}
    initial_state = {"task": "Asking for a server upgrade budget"}
    
    print("\n[Phase 1: Starting Agent]")
    # Notice we use .stream or .invoke. It will run drafter, and pause.
    graph.invoke(initial_state, config)

    # 4. Check current state and intercept for human review
    current_state = graph.get_state(config)
    print("\n--- ✋ Graph Paused! Human Review Required ---")
    print("Draft generated:")
    print("-" * 30)
    print(current_state.values.get("email_draft", "No draft found."))
    print("-" * 30)
    
    user_input = input("Do you approve this draft to be sent? (yes/no): ")
    
    # 5. Update graph state with human feedback
    is_approved = user_input.lower() in ["y", "yes"]
    
    # We use update_state to artificially inject data into the paused graph memory
    graph.update_state(config, {"is_approved": is_approved})
    
    # 6. Resume execution!
    # Calling invoke with NO input data tells LangGraph "resume where you left off"
    print("\n[Phase 2: Resuming Graph Execution]")
    graph.invoke(None, config)

    print("\n--- 🧠 Why we did this ---")
    print("You NEVER want an autonomous agent executing dangerous code, spending ")
    print("money, or sending emails to your boss without human oversight.")
    print("LangGraph's checkpointing system allows you to build completely asynchronous")
    print("approvals: The graph pauses, saves to a database, and weeks later when a ")
    print("human clicks 'Approve' on a web UI, the python script resumes perfectly.")

if __name__ == "__main__":
    main()
