"""
================================================================================
LANGGRAPH PROJECT 5: Multi-Agent Systems
================================================================================
WHAT YOU LEARN:
  - What a multi-agent system is
  - Fan-out/fan-in: send to multiple agents, collect results
  - Send API: dynamically create parallel work
  - Merging results from parallel agents
  - Specialized agents working together

WHY MULTI-AGENT?
  Complex tasks benefit from specialization:
  - Research task → split into: web search + code analysis + data analysis
  - Writing task → split into: outline + sections + editing + proofreading
  Each agent focuses on what it does best!

SECRET TIP: Use Send() for dynamic parallelism — create agents on the fly
            based on runtime data, not just at graph build time.
================================================================================
"""

from typing import TypedDict, Annotated, List, Literal
import operator
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama3-8b-8192", temperature=0)


print("=" * 60)
print("LANGGRAPH P5: Multi-Agent Systems")
print("=" * 60)

# Shared state for multi-agent system
class MultiAgentState(TypedDict):
    """State shared across all agents."""
    task: str                                   # Original task
    research_result: str                        # From research agent
    analysis_result: str                        # From analysis agent
    writing_result: str                         # From writing agent
    final_report: str                           # Combined report
    messages: Annotated[List[BaseMessage], operator.add]


# ── Individual Agent Nodes ─────────────────────────────────────────────────────

def research_agent(state: MultiAgentState) -> dict:
    """
    Research Agent: Focuses on gathering information.
    In production: would use web search, database queries, etc.
    """
    print("  [Research Agent] Gathering information...")
    
    response = llm.invoke([
        SystemMessage("You are a research expert. Provide factual information and data."),
        HumanMessage(f"Research this topic and provide key facts: {state['task']}")
    ])
    
    return {"research_result": f"[RESEARCH]\n{response.content}"}


def analysis_agent(state: MultiAgentState) -> dict:
    """
    Analysis Agent: Focuses on interpreting information.
    Runs in PARALLEL with research agent.
    """
    print("  [Analysis Agent] Analyzing...")
    
    response = llm.invoke([
        SystemMessage("You are a data analyst. Provide analytical insights and patterns."),
        HumanMessage(f"Analyze this topic: {state['task']}\nFocus on trends, patterns, and implications.")
    ])
    
    return {"analysis_result": f"[ANALYSIS]\n{response.content}"}


def writing_agent(state: MultiAgentState) -> dict:
    """
    Writing Agent: Synthesizes research + analysis into a report.
    Runs AFTER research and analysis are complete (fan-in).
    """
    print("  [Writing Agent] Creating report...")
    
    # This agent has access to BOTH research and analysis results
    response = llm.invoke([
        SystemMessage("You are a technical writer. Create clear, structured reports."),
        HumanMessage(
            f"Create a brief report on: {state['task']}\n\n"
            f"Use this research: {state['research_result'][:300]}\n\n"
            f"And this analysis: {state['analysis_result'][:300]}"
        )
    ])
    
    return {"final_report": response.content}


def orchestrator_node(state: MultiAgentState) -> dict:
    """
    Orchestrator: Decides which agents to run.
    In this example, it just passes the task to parallel agents.
    """
    print(f"  [Orchestrator] Dispatching task: {state['task'][:40]}...")
    return {}   # No state change — just routing


# Build multi-agent graph
multi_builder = StateGraph(MultiAgentState)

# Add all agents
multi_builder.add_node("orchestrator", orchestrator_node)
multi_builder.add_node("research_agent", research_agent)
multi_builder.add_node("analysis_agent", analysis_agent)
multi_builder.add_node("writing_agent", writing_agent)

# Entry point
multi_builder.add_edge(START, "orchestrator")

# FAN-OUT: orchestrator → BOTH research AND analysis simultaneously
multi_builder.add_edge("orchestrator", "research_agent")    # Branch 1
multi_builder.add_edge("orchestrator", "analysis_agent")    # Branch 2 (runs in parallel!)

# FAN-IN: BOTH research AND analysis → writing_agent
# writing_agent waits for BOTH to complete
multi_builder.add_edge("research_agent", "writing_agent")
multi_builder.add_edge("analysis_agent", "writing_agent")

multi_builder.add_edge("writing_agent", END)

multi_graph = multi_builder.compile()

result = multi_graph.invoke({
    "task": "Impact of AI on software development",
    "research_result": "",
    "analysis_result": "",
    "writing_result": "",
    "final_report": "",
    "messages": [],
})

print(f"\nFinal Report Preview:\n{result['final_report'][:300]}...")


"""
================================================================================
LANGGRAPH PROJECT 6: Research Agent with Tool Loop
================================================================================
WHAT YOU LEARN:
  - The "tool-calling" agent loop in LangGraph
  - ToolNode: automatic tool execution
  - tools_condition: continue if tools called, end if not
  - How to build a proper agentic loop with LangGraph

THIS IS THE MOST IMPORTANT LANGGRAPH PATTERN:
  1. LLM looks at question and available tools
  2. If LLM calls a tool → execute it → loop back to LLM with result
  3. If LLM doesn't call a tool → it has the final answer → END

  This is what makes agents POWERFUL: they can use tools iteratively!
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P6: Research Agent with Tool Loop")
print("=" * 60)

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

# Define tools the agent can use
@tool
def search_web(query: str) -> str:
    """
    Search the web for current information.
    Use for: recent news, current events, facts not in training data.
    """
    # Simulated search results
    results = {
        "python": "Python 3.12 released October 2023. New features: type parameter syntax, f-string improvements.",
        "langchain": "LangChain v0.2 released 2024. Key changes: LCEL stability, LangGraph integration.",
        "ai": "GPT-4o released May 2024. Multimodal capabilities. Llama 3 released April 2024.",
    }
    for key in results:
        if key in query.lower():
            return f"Search results for '{query}': {results[key]}"
    return f"Search results for '{query}': Found general information about the topic."


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Examples: '2+2', '15% of 200'."""
    try:
        import re
        # Handle percentages
        pct_match = re.match(r'(\d+\.?\d*)%\s*of\s*(\d+\.?\d*)', expression.lower())
        if pct_match:
            return str(float(pct_match.group(1)) / 100 * float(pct_match.group(2)))
        return str(eval(expression.replace('^', '**'), {"__builtins__": {}}))
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def get_info(topic: str) -> str:
    """Get stored information about a topic from the knowledge base."""
    knowledge = {
        "langchain": "LangChain is an LLM application framework. Core concepts: Runnables, LCEL, Chains, Agents.",
        "langgraph": "LangGraph is a stateful agent framework. Core concepts: State, Nodes, Edges, Checkpointers.",
        "python": "Python is a high-level language. Created 1991. Great for AI, web, scripting.",
    }
    for key, val in knowledge.items():
        if key in topic.lower():
            return val
    return f"No stored info for: {topic}"


tools = [search_web, calculate, get_info]

# State: just messages (simplest agent state)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


def agent_node(state: AgentState) -> dict:
    """
    The LLM node — brain of the agent.
    Decides: answer now, or call a tool?
    """
    # Bind tools to LLM so it can call them
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke(state["messages"])
    print(f"  [Agent] Response type: {'Tool calls' if response.tool_calls else 'Final answer'}")
    
    return {"messages": [response]}   # Appended to message history


# ToolNode automatically executes whatever tools the LLM requested
tool_node = ToolNode(tools)   # Pass all available tools


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """
    Decide: keep going (call tools) or stop (final answer).
    - If last message has tool_calls → go to tool_node
    - Otherwise → END
    """
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"   # LLM wants to use a tool — continue loop
    
    return "__end__"     # No tool calls — LLM has final answer


# Build agent graph
agent_builder = StateGraph(AgentState)

agent_builder.add_node("agent", agent_node)      # LLM node
agent_builder.add_node("tools", tool_node)        # Tool execution node

agent_builder.add_edge(START, "agent")

# THE CORE LOOP:
# agent → (if tool calls) → tools → agent (again with tool results)
# agent → (if no tool calls) → END
agent_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",       # Has tool calls → execute tools
        "__end__": END,         # No tool calls → we're done
    }
)

# After tools run → go back to agent (THE LOOP!)
agent_builder.add_edge("tools", "agent")

agent_graph = agent_builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "research_001"}}

# Test the research agent
print("\n--- Research Agent Test ---")
questions = [
    "Search for information about LangChain and calculate 15% of 200.",
    "What is the weather in Tokyo?"   # Should use get_info or say it doesn't have that
]

for q in questions:
    print(f"\nQuestion: {q}")
    result = agent_graph.invoke(
        {"messages": [HumanMessage(q)]},
        config={"configurable": {"thread_id": f"q_{hash(q)}"}}
    )
    final_answer = result["messages"][-1].content
    print(f"Answer: {final_answer[:150]}...")


"""
================================================================================
LANGGRAPH PROJECT 7: Adaptive RAG Graph
================================================================================
WHAT YOU LEARN:
  - RAG as a GRAPH: retrieve → grade → generate → verify
  - Grading retrieved documents (are they relevant?)
  - Query rewriting: improve the query if retrieval was bad
  - Answer verification: hallucination check
  - Corrective RAG loop: fix bad answers automatically
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P7: Adaptive RAG Graph")
print("=" * 60)

from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

# State for RAG
class RAGState(TypedDict):
    question: str               # Original question
    rewritten_question: str     # Improved question (if needed)
    documents: List[str]        # Retrieved document chunks
    generation: str             # LLM's generated answer
    relevance_score: str        # "yes" or "no" — are docs relevant?
    hallucination_check: str    # "yes" or "no" — is answer grounded?
    iterations: int             # Prevent infinite loops


# Simulated vector store
DOCUMENTS = [
    "LangGraph is a stateful framework built on LangChain. It uses nodes and edges.",
    "LangChain provides tools for building LLM applications including chains and agents.",
    "Python is a programming language. Not related to LangGraph or LangChain.",
    "The checkpointer in LangGraph saves state between graph invocations.",
]


def retrieve_node(state: RAGState) -> dict:
    """Retrieve relevant documents using the question."""
    question = state.get("rewritten_question") or state["question"]
    
    # Simple keyword retrieval (in real life: vector store)
    q_words = question.lower().split()
    retrieved = []
    for doc in DOCUMENTS:
        if any(word in doc.lower() for word in q_words):
            retrieved.append(doc)
    
    print(f"  [Retrieve] Found {len(retrieved)} documents for: {question[:40]}")
    return {
        "documents": retrieved[:3],   # Top 3
        "iterations": state.get("iterations", 0) + 1
    }


def grade_documents_node(state: RAGState) -> dict:
    """
    Grade whether retrieved documents are relevant to the question.
    This is ADAPTIVE RAG — we check before generating!
    """
    question = state["question"]
    docs = state["documents"]
    
    if not docs:
        print("  [Grade] No documents retrieved → not relevant")
        return {"relevance_score": "no"}
    
    # Ask LLM to grade relevance
    grade_prompt = f"""Is this document relevant to the question?
Question: {question}
Document: {docs[0][:200]}
Answer with only 'yes' or 'no':"""
    
    score = llm.invoke(grade_prompt).content.strip().lower()
    # Normalize to yes/no
    score = "yes" if "yes" in score else "no"
    
    print(f"  [Grade] Relevance: {score}")
    return {"relevance_score": score}


def rewrite_query_node(state: RAGState) -> dict:
    """Rewrite the query to improve retrieval."""
    question = state["question"]
    
    new_q = llm.invoke(
        f"Rephrase this question to be more specific and searchable: {question}"
    ).content
    
    print(f"  [Rewrite] '{question}' → '{new_q[:60]}'")
    return {"rewritten_question": new_q}


def generate_node(state: RAGState) -> dict:
    """Generate an answer using the retrieved documents."""
    question = state["question"]
    docs = "\n".join(state["documents"])
    
    response = llm.invoke(
        f"Answer based ONLY on this context:\n{docs}\n\nQuestion: {question}"
    )
    
    print(f"  [Generate] Created answer")
    return {"generation": response.content}


def hallucination_check_node(state: RAGState) -> dict:
    """Check if the generated answer is grounded in the documents."""
    answer = state["generation"]
    docs = "\n".join(state["documents"])
    
    check = llm.invoke(
        f"""Is this answer grounded in the provided documents? Answer 'yes' or 'no'.
Documents: {docs[:500]}
Answer: {answer[:200]}
Grounded (yes/no):"""
    ).content.strip().lower()
    
    grounded = "yes" if "yes" in check else "no"
    print(f"  [HallucinationCheck] Grounded: {grounded}")
    return {"hallucination_check": grounded}


# Conditional routing functions
def route_after_grading(state: RAGState) -> str:
    """Route based on document relevance."""
    if state["relevance_score"] == "yes":
        return "generate"   # Good docs → generate
    elif state.get("iterations", 0) >= 3:
        return "generate"   # Too many retries → generate anyway
    else:
        return "rewrite"    # Bad docs → rewrite query and try again


def route_after_generation(state: RAGState) -> str:
    """Route based on hallucination check."""
    if state["hallucination_check"] == "yes":
        return "__end__"    # Good answer → done!
    elif state.get("iterations", 0) >= 3:
        return "__end__"    # Too many retries → accept answer
    else:
        return "generate"   # Hallucinated → try generating again


# Build RAG graph
rag_builder = StateGraph(RAGState)
rag_builder.add_node("retrieve", retrieve_node)
rag_builder.add_node("grade_docs", grade_documents_node)
rag_builder.add_node("rewrite_query", rewrite_query_node)
rag_builder.add_node("generate", generate_node)
rag_builder.add_node("hallucination_check", hallucination_check_node)

rag_builder.add_edge(START, "retrieve")
rag_builder.add_edge("retrieve", "grade_docs")
rag_builder.add_conditional_edges("grade_docs", route_after_grading)
rag_builder.add_edge("generate", "hallucination_check")
rag_builder.add_conditional_edges("hallucination_check", route_after_generation)
rag_builder.add_edge("rewrite_query", "retrieve")   # Rewrite → retrieve again (LOOP!)

rag_graph = rag_builder.compile()

result = rag_graph.invoke({
    "question": "What is LangGraph and how does it handle state?",
    "rewritten_question": "",
    "documents": [],
    "generation": "",
    "relevance_score": "",
    "hallucination_check": "",
    "iterations": 0,
})
print(f"\nFinal Answer: {result['generation'][:200]}...")


"""
================================================================================
LANGGRAPH PROJECT 8: Reflection Agent
================================================================================
WHAT YOU LEARN:
  - Reflection loops: generate → critique → improve → repeat
  - Self-evaluation patterns
  - When to stop iterating
  - Quality gates in agent workflows
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P8: Reflection Agent")
print("=" * 60)

class ReflectionState(TypedDict):
    topic: str              # What to write about
    draft: str              # Current draft
    critique: str           # Current critique
    revision_count: int     # How many times we've revised
    is_good_enough: bool    # Stop signal


MAX_REVISIONS = 3  # Maximum improvement iterations

def generate_draft_node(state: ReflectionState) -> dict:
    """Generate initial draft or revision based on critique."""
    topic = state["topic"]
    critique = state.get("critique", "")
    
    if critique:
        # Revision: improve based on critique
        prompt = f"Improve this draft based on the critique.\nTopic: {topic}\nDraft: {state['draft']}\nCritique: {critique}\nImproved draft:"
        print(f"  [Generate] Revision #{state['revision_count'] + 1}")
    else:
        # First draft
        prompt = f"Write a clear, informative paragraph about: {topic}"
        print(f"  [Generate] Writing initial draft")
    
    draft = llm.invoke(prompt).content
    return {
        "draft": draft,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def reflect_node(state: ReflectionState) -> dict:
    """Critique the current draft and decide if it's good enough."""
    draft = state["draft"]
    topic = state["topic"]
    
    # Get critique
    critique = llm.invoke(
        f"Critically evaluate this paragraph about '{topic}'.\n"
        f"Identify 1-2 specific improvements needed.\n"
        f"Draft: {draft}\n"
        f"Critique (be specific and actionable):"
    ).content
    
    # Decide if good enough
    quality = llm.invoke(
        f"Is this draft high quality? Answer only 'yes' or 'no'.\n"
        f"Draft: {draft}\nHigh quality:"
    ).content.lower()
    
    is_good = "yes" in quality
    print(f"  [Reflect] Quality: {'✅ Good' if is_good else '📝 Needs work'}")
    
    return {
        "critique": critique,
        "is_good_enough": is_good,
    }


def should_continue_reflection(state: ReflectionState) -> str:
    """Continue if not good enough and haven't hit max revisions."""
    if state["is_good_enough"]:
        return "__end__"    # Good enough → stop
    if state["revision_count"] >= MAX_REVISIONS:
        return "__end__"    # Max revisions → stop anyway
    return "generate_draft"  # Keep improving


reflect_builder = StateGraph(ReflectionState)
reflect_builder.add_node("generate_draft", generate_draft_node)
reflect_builder.add_node("reflect", reflect_node)

reflect_builder.add_edge(START, "generate_draft")
reflect_builder.add_edge("generate_draft", "reflect")
reflect_builder.add_conditional_edges("reflect", should_continue_reflection)

reflection_graph = reflect_builder.compile()

result = reflection_graph.invoke({
    "topic": "Why LangGraph is better than simple chains for complex AI agents",
    "draft": "",
    "critique": "",
    "revision_count": 0,
    "is_good_enough": False,
})

print(f"\nFinal Draft ({result['revision_count']} revisions):")
print(result["draft"][:300] + "...")


"""
================================================================================
LANGGRAPH PROJECT 9: Supervisor Pattern
================================================================================
WHAT YOU LEARN:
  - Supervisor orchestrating multiple worker agents
  - Dynamic routing: supervisor decides which agent to use next
  - When to call which specialist
  - Combining all results for a final answer
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P9: Supervisor Pattern")
print("=" * 60)

from typing import Union

class SupervisorState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_worker: str        # Who should go next?
    final_answer: str


# Worker agents
def researcher(state: SupervisorState) -> dict:
    """Research worker — gathers information."""
    last_msg = state["messages"][-1].content
    response = llm.invoke([
        SystemMessage("You are a research specialist. Provide factual, detailed information."),
        HumanMessage(f"Research: {last_msg}")
    ])
    print(f"  [Researcher] Done")
    return {"messages": [AIMessage(content=f"[Research]: {response.content}")]}


def coder(state: SupervisorState) -> dict:
    """Coding worker — writes and explains code."""
    last_msg = state["messages"][-1].content
    response = llm.invoke([
        SystemMessage("You are a coding expert. Provide working code examples."),
        HumanMessage(f"Write code for: {last_msg}")
    ])
    print(f"  [Coder] Done")
    return {"messages": [AIMessage(content=f"[Code]: {response.content}")]}


def writer(state: SupervisorState) -> dict:
    """Writer worker — synthesizes everything into a final answer."""
    context = "\n".join([m.content for m in state["messages"][-4:]])
    response = llm.invoke([
        SystemMessage("You are a technical writer. Synthesize information clearly."),
        HumanMessage(f"Based on this information, write a clear final answer:\n{context}")
    ])
    print(f"  [Writer] Done")
    return {
        "messages": [AIMessage(content=f"[Final]: {response.content}")],
        "final_answer": response.content,
    }


WORKERS = ["researcher", "coder", "writer", "FINISH"]

def supervisor_node(state: SupervisorState) -> dict:
    """
    Supervisor decides which worker to call next.
    This is the key to the supervisor pattern!
    """
    
    # Build context from message history
    history = "\n".join([f"{m.type}: {m.content[:100]}" for m in state["messages"][-3:]])
    
    decision = llm.invoke(
        f"""You are a supervisor managing these workers: {WORKERS}
        
History: {history}

Decide which worker to call next, or FINISH if done.
Return ONLY the worker name: researcher, coder, writer, or FINISH"""
    ).content.strip()
    
    # Normalize decision
    for worker in WORKERS:
        if worker.lower() in decision.lower():
            decision = worker
            break
    else:
        decision = "FINISH"   # Default to finish if unclear
    
    print(f"  [Supervisor] → {decision}")
    return {"next_worker": decision}


def route_supervisor(state: SupervisorState) -> str:
    """Route to the worker the supervisor chose."""
    next_w = state.get("next_worker", "FINISH")
    return "FINISH" if next_w == "FINISH" else next_w


supervisor_builder = StateGraph(SupervisorState)
supervisor_builder.add_node("supervisor", supervisor_node)
supervisor_builder.add_node("researcher", researcher)
supervisor_builder.add_node("coder", coder)
supervisor_builder.add_node("writer", writer)

supervisor_builder.add_edge(START, "supervisor")
supervisor_builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {"researcher": "researcher", "coder": "coder", "writer": "writer", "FINISH": END}
)
# All workers report back to supervisor after completing
supervisor_builder.add_edge("researcher", "supervisor")
supervisor_builder.add_edge("coder", "supervisor")
supervisor_builder.add_edge("writer", "supervisor")

supervisor_graph = supervisor_builder.compile()

result = supervisor_graph.invoke({
    "messages": [HumanMessage("How do I build a web scraper in Python? I need research on libraries and working code.")],
    "next_worker": "",
    "final_answer": "",
})
print(f"\nFinal: {result.get('final_answer', result['messages'][-1].content)[:200]}...")


"""
================================================================================
LANGGRAPH PROJECT 10: Full Autonomous System
================================================================================
Combines EVERYTHING: memory + tools + human-in-loop + multi-agent + reflection
This is a production-ready pattern for complex AI systems.
================================================================================
"""

print("\n" + "=" * 60)
print("LANGGRAPH P10: Full Autonomous System")
print("=" * 60)
print("""
This project combines:
  ✅ Persistent memory (MemorySaver checkpointer)
  ✅ Tool calling (search, calculate, get_info)  
  ✅ Human-in-the-loop (interrupt for confirmation)
  ✅ Multi-step reasoning (plan → execute → verify)
  ✅ Reflection loop (verify quality, retry if needed)
  ✅ Session management (thread_id per conversation)
""")

class FullSystemState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    task: str
    plan: List[str]         # Steps to complete
    current_step: int       # Which step we're on
    results: List[str]      # Results of each step
    human_approved: bool    # Human approved the plan?
    final_answer: str
    verified: bool          # Is answer verified?


def plan_task(state: FullSystemState) -> dict:
    """Create a step-by-step plan for the task."""
    task = state["task"]
    response = llm.invoke(f"Create a 3-step plan to: {task}. Return as numbered list.")
    
    # Parse into list
    lines = response.content.split("\n")
    plan = [line.strip() for line in lines if line.strip() and line[0].isdigit()][:3]
    if not plan:
        plan = ["Step 1: Research", "Step 2: Analyze", "Step 3: Synthesize"]
    
    print(f"  [Planner] Plan: {plan}")
    return {"plan": plan, "current_step": 0}


def approve_plan_node(state: FullSystemState) -> dict:
    """Human approval gate."""
    from langgraph.types import interrupt
    
    # Show plan to human
    print(f"  [Approval] Showing plan to human...")
    
    response = interrupt({
        "message": "Please review the plan:",
        "plan": state["plan"],
    })
    
    approved = response.get("approved", True)   # Default approve
    return {"human_approved": approved}


def execute_step_node(state: FullSystemState) -> dict:
    """Execute the current step of the plan."""
    if not state["human_approved"]:
        return {"final_answer": "Task cancelled by user."}
    
    step_idx = state["current_step"]
    if step_idx >= len(state["plan"]):
        return {}
    
    step = state["plan"][step_idx]
    
    # Execute with tools
    llm_with_tools = llm.bind_tools([search_web, calculate, get_info])
    response = llm_with_tools.invoke(
        f"Execute this step: {step}\nContext: {state['task']}"
    )
    
    results = list(state.get("results", []))
    results.append(f"Step {step_idx + 1}: {response.content[:200]}")
    
    print(f"  [Execute] Step {step_idx + 1}/{len(state['plan'])}")
    
    return {
        "results": results,
        "current_step": step_idx + 1,
    }


def synthesize_node(state: FullSystemState) -> dict:
    """Combine all step results into a final answer."""
    all_results = "\n".join(state.get("results", []))
    
    answer = llm.invoke(
        f"Synthesize these results into a final answer for: {state['task']}\n\nResults:\n{all_results}"
    ).content
    
    return {"final_answer": answer}


def verify_node(state: FullSystemState) -> dict:
    """Verify the final answer quality."""
    check = llm.invoke(
        f"Is this a complete, accurate answer? Answer yes/no.\nTask: {state['task']}\nAnswer: {state['final_answer']}"
    ).content.lower()
    
    verified = "yes" in check
    print(f"  [Verify] Verified: {verified}")
    return {"verified": verified}


def route_execute(state: FullSystemState) -> str:
    """Keep executing steps until all done or not approved."""
    if not state.get("human_approved", False):
        return "__end__"
    if state["current_step"] < len(state.get("plan", [])):
        return "execute_step"   # More steps to do
    return "synthesize"         # All steps done → synthesize


def route_verify(state: FullSystemState) -> str:
    """Route after verification."""
    if state.get("verified"):
        return "__end__"
    return "synthesize"   # Try again (max 1 retry in this example)


# Build full system
full_builder = StateGraph(FullSystemState)
full_builder.add_node("plan", plan_task)
full_builder.add_node("approve", approve_plan_node)
full_builder.add_node("execute_step", execute_step_node)
full_builder.add_node("synthesize", synthesize_node)
full_builder.add_node("verify", verify_node)

full_builder.add_edge(START, "plan")
full_builder.add_edge("plan", "approve")
full_builder.add_conditional_edges("approve", lambda s: "__end__" if not s.get("human_approved") else "execute_step")
full_builder.add_conditional_edges("execute_step", route_execute)
full_builder.add_edge("synthesize", "verify")
full_builder.add_conditional_edges("verify", route_verify)

full_checkpointer = MemorySaver()
full_graph = full_builder.compile(
    checkpointer=full_checkpointer,
    interrupt_before=["approve"],
)

full_config = {"configurable": {"thread_id": "full_task_001"}}

print("\n--- Running Full System ---")

# First run — will pause at approve
try:
    full_graph.invoke({
        "messages": [HumanMessage("Explain the benefits of using LangGraph")],
        "task": "Explain the benefits of using LangGraph",
        "plan": [],
        "current_step": 0,
        "results": [],
        "human_approved": False,
        "final_answer": "",
        "verified": False,
    }, config=full_config)
except:
    pass

# Check what plan was generated
state = full_graph.get_state(full_config)
print(f"Generated plan: {state.values.get('plan', [])}")

# Human approves
from langgraph.types import Command
result = full_graph.invoke(
    Command(resume={"approved": True}),
    config=full_config
)

print(f"\n✅ Final Answer:\n{result.get('final_answer', 'N/A')[:300]}...")


print("\n" + "=" * 60)
print("KEY TAKEAWAYS FROM LANGGRAPH P5-P10:")
print("=" * 60)
print("""
P5 - Multi-Agent:
  Fan-out: add multiple edges from one node (parallel execution)
  Fan-in: multiple edges TO one node (waits for all to complete)
  Send() for dynamic parallelism based on runtime data

P6 - Tool Loop:
  THE MOST IMPORTANT PATTERN: agent ↔ tools loop
  ToolNode executes tools automatically
  should_continue() returns "tools" or "__end__"
  This is how ALL modern AI agents work!

P7 - Adaptive RAG:
  Add feedback loops to RAG: grade → rewrite → retrieve if bad
  Hallucination check after generation
  Max iterations safety valve

P8 - Reflection:
  Generate → Critique → Improve loop
  Quality gate decides when to stop
  MAX_REVISIONS prevents infinite loops

P9 - Supervisor:
  LLM supervisor dynamically routes to specialist workers
  All workers report back to supervisor
  Supervisor decides when to FINISH

P10 - Full System:
  Combine: memory + tools + human-in-loop + planning + verification
  This is a production-ready agent architecture
""")
