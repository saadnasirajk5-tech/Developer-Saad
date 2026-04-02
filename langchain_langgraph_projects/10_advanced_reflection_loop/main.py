import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

load_dotenv(dotenv_path='../.env')

# 1. State
class ReflectState(TypedDict):
    task: str
    code_generated: str
    error_message: str
    attempts: int

# 2. Nodes
def code_generator_node(state: ReflectState):
    print("--- 💻 Generator Node Playing ---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    # If there is an error message, we are in a reflection loop! We must tell the LLM.
    if state.get("error_message"):
        print(f"    [Self-Correcting: Attempt #{state['attempts'] + 1}]")
        prompt = (f"You were asked to write code for: {state['task']}.\n"
                  f"Your last code failed with this error: {state['error_message']}\n"
                  f"Please fix the code and output ONLY python code. No markdown formatting.")
    else:
        print(f"    [Initial Generation]")
        prompt = f"Write python code for: {state['task']}. Output ONLY valid python code. No markdown formatting."
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Strip markdown block ticks if the AI included them anyway
    cleaned_code = response.content.replace("```python", "").replace("```", "").strip()
    
    # Increment attempts
    current_attempts = state.get("attempts", 0) + 1
    
    return {"code_generated": cleaned_code, "attempts": current_attempts}

def test_executor_node(state: ReflectState):
    print("--- 🧪 Test Executor Node Running ---")
    code = state["code_generated"]
    
    # DANGEROUS: Just for the purpose of this tutorial, we will use 'exec' to run 
    # the LLM output locally to see if it works. In a real app, use a sandboxed Docker container!
    try:
        # We define a dummy namespace
        namespace = {}
        exec(code, namespace) # Executes the python code string
        
        # If it runs without throwing a python error, we consider it a success!
        print("    [Test Passed!]")
        return {"error_message": ""} # Error is empty string
        
    except Exception as e:
        # Catch errors like SyntaxError, NameError, etc.
        error_str = f"{type(e).__name__}: {str(e)}"
        print(f"    [Test Failed with Error: {error_str}]")
        return {"error_message": error_str}

def router(state: ReflectState):
    # Check if we hit the maximum attempts limit (to prevent infinite loops)
    if state["attempts"] >= 3:
        print("    [Router: Max attempts reached, ending.]")
        return "end"
    
    # Did the test executor find an error?
    if state["error_message"] == "":
        print("    [Router: Code worked, ending successfully.]")
        return "end"
    else:
        print("    [Router: Errors found, looping BACK to generator!]")
        return "loop_to_generator"

def main():
    print("🚀 Starting Advanced Reflection Loop Flow")

    # 3. Build the Graph
    builder = StateGraph(ReflectState)

    builder.add_node("generator", code_generator_node)
    builder.add_node("tester", test_executor_node)

    # 4. Define cyclic flow 
    builder.add_edge(START, "generator")
    builder.add_edge("generator", "tester")
    
    # Tester routes based on success or failure!
    builder.add_conditional_edges(
        "tester",
        router,
        {
            "end": END,
            "loop_to_generator": "generator" # Loops backwards! Cyclic graph!
        }
    )

    graph = builder.compile()

    # Let's give it a trick task that often causes syntax errors or imports to miss
    initial_state = {
        "task": "Write a function 'compute_square_root' that takes a number, and if it is negative, it raises a explicit ValueError, otherwise returns the square root using the python math library. Then call it securely with the number 16.",
        "error_message": "",
        "attempts": 0
    }
    
    print("\n--- Execution Start ---")
    final_output = graph.invoke(initial_state)

    print("\n================ FINAL REPORT ================")
    if final_output["error_message"]:
        print("❌ Agent Failed to solve the problem.")
        print(f"Last Error: {final_output['error_message']}")
    else:
        print("✅ Program written and executed successfully!")
        print("\nGenerated Code:")
        print("-" * 30)
        print(final_output["code_generated"])
        print("-" * 30)
    print("==============================================")
    
    print("\n--- 🧠 Why we did this ---")
    print("Large language models make mistakes. Instead of complex prompt engineering to ")
    print("try to force perfect zero-shot results, the paradigm has shifted. We now ")
    print("build fast architectures that EXPECT errors. By chaining generators directly ")
    print("into compilers/checkers, the agent can see its own mistakes and try again.")
    print("This 'Self-Reflection' dramatically increases the intelligence ceiling of AI.")

if __name__ == "__main__":
    main()
