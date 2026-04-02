import os
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableBranch, RunnableLambda

load_dotenv(dotenv_path='../.env')

def main():
    print("🚀 Starting Complex Chains and Routing")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # 1. Define Specific Prompts/Chains for distinct topics
    
    # Chain A: Tech Support
    tech_template = """You are an expert tech support representative.
    Respond nicely and provide technical troubleshooting steps.
    User specifies: {input}
    """
    tech_chain = PromptTemplate.from_template(tech_template) | llm | StrOutputParser()

    # Chain B: Billing Support
    billing_template = """You are a polite billing agent.
    You help with refunds and invoices. Be very apologetic.
    User specifies: {input}
    """
    billing_chain = PromptTemplate.from_template(billing_template) | llm | StrOutputParser()

    # Chain C: General Conversational (Fallback)
    general_chain = PromptTemplate.from_template("Be remarkably witty and answer: {input}") | llm | StrOutputParser()

    # 2. Build the Concept Router
    # Let's ask an LLM to categorize the intent first!
    router_template = """Given the user's input, classify it as either 'tech', 'billing', or 'general'.
    DO NOT respond with anything else except that single word.
    
    Input: {input}
    Classification:"""
    
    router_chain = (
        PromptTemplate.from_template(router_template) 
        | llm 
        | StrOutputParser()
        | (lambda x: x.strip().lower()) # Clean up parsing
    )

    # 3. Create the Routing Logic (RunnableBranch)
    # RunnableBranch evaluates conditions in order. If true, run that chain.
    branch = RunnableBranch(
        # Condition 1: If router says 'tech', run tech_chain
        (lambda x: x["topic"] == "tech", tech_chain),
        # Condition 2: If router says 'billing', run billing_chain
        (lambda x: x["topic"] == "billing", billing_chain),
        # Default fallback
        general_chain
    )

    # 4. Tie it into a unified chain
    # We use RunnableLambda to create a dictionary with 'topic' and the original 'input'
    def route_to_branch(inputs):
        # inputs is the string question
        topic = router_chain.invoke({"input": inputs})
        print(f"  [Router Decision: Sent to '{topic}' department]")
        return {"topic": topic, "input": inputs}

    full_chain = RunnableLambda(route_to_branch) | branch

    # 5. Let's test it out!
    queries = [
        "My computer screen is completely black and making a beep sound.",
        "I need a refund! You charged me twice this month!",
        "What is the airspeed velocity of an unladen swallow?"
    ]

    for q in queries:
        print(f"\n--- User: {q} ---")
        answer = full_chain.invoke(q)
        print(f"🤖 AI:\n{answer}")

    print("\n--- 🧠 Why we did this ---")
    print("Instead of having one giant multi-purpose LLM prompt that tries to do everything ")
    print("poorly, we use a concept called 'Semantic Routing'. We use a smaller/fast LLM call ")
    print("to figure out the intent, then route the user to a highly specialized, optimized ")
    print("chain that handles only that task. This creates much more reliable applications.")

if __name__ == "__main__":
    main()
