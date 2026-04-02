"""
================================================================================
PROJECT 3: LangChain Expression Language (LCEL) — Chains
================================================================================
WHAT YOU LEARN:
  - The | pipe operator: chaining runnables together
  - RunnablePassthrough: Pass input unchanged through the chain
  - RunnableLambda: Wrap any Python function as a Runnable
  - RunnableParallel: Run multiple chains at the same time
  - itemgetter: Pick specific keys from dicts
  - StrOutputParser: Convert AIMessage → plain string
  - Branching with RunnableBranch
  - Fallback chains for error handling

THE BIG IDEA — LCEL:
  Everything in LangChain is a "Runnable" with .invoke/.stream/.batch
  The | operator COMPOSES Runnables: output of left → input of right
  
  prompt | llm | parser    means:
    1. prompt.invoke(input)     → formatted messages
    2. llm.invoke(messages)     → AIMessage
    3. parser.invoke(AIMessage) → string

SECRET TIP: LCEL chains are lazy — nothing runs until .invoke() is called.
            This means you can BUILD chains without executing them.
================================================================================
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser   # AIMessage → string
from langchain_core.runnables import (
    RunnablePassthrough,    # Pass input through unchanged
    RunnableLambda,         # Wrap any Python function
    RunnableParallel,       # Run branches in parallel
    RunnableBranch,         # Conditional branching
)
from operator import itemgetter     # Pick dict keys cleanly
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="llama3-8b-8192", temperature=0)
parser = StrOutputParser()   # Converts AIMessage → plain Python string


# ── LESSON 1: Basic Pipe Chain ────────────────────────────────────────────────
print("=" * 60)
print("LESSON 1: Basic prompt | llm | parser chain")
print("=" * 60)

# The most common LangChain pattern: 3 components connected with |
basic_chain = (
    ChatPromptTemplate.from_template("What is {topic}? One sentence.")
    | llm           # Prompt output (messages) → LLM
    | parser        # LLM output (AIMessage) → plain string
)

# .invoke() runs the entire chain and returns a STRING
result = basic_chain.invoke({"topic": "quantum entanglement"})
print(f"Result type: {type(result)}")   # <class 'str'> — not AIMessage!
print(f"Result: {result}")

# 💡 You can also stream the whole chain!
print("\nStreaming chain: ", end="")
for chunk in basic_chain.stream({"topic": "black holes"}):
    print(chunk, end="", flush=True)    # chunk is now a plain string chunk
print()


# ── LESSON 2: RunnablePassthrough ────────────────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 2: RunnablePassthrough — passing data through")
print("=" * 60)

# When a chain expects a dict, use RunnablePassthrough to keep original inputs
# while adding new computed values

retrieval_chain = (
    # Step 1: Pass through and add "context" key
    RunnablePassthrough.assign(
        # .assign() adds NEW keys to the dict without removing existing ones
        word_count=lambda x: len(x["question"].split()),   # Count words in question
        upper_q=lambda x: x["question"].upper(),           # Uppercase version
    )
    | RunnableLambda(lambda x: {
        # Now x has: question, word_count, upper_q
        "question": x["question"],
        "context": f"[context for: {x['upper_q']}]",
        "word_count": x["word_count"]
    })
    | ChatPromptTemplate.from_template(
        "Context: {context}\nQ: {question}\nAnswer briefly:"
    )
    | llm
    | parser
)

result = retrieval_chain.invoke({"question": "What is gravity?"})
print(f"Result: {result[:200]}")


# ── LESSON 3: RunnableLambda — Wrap Any Function ──────────────────────────────
print("\n" + "=" * 60)
print("LESSON 3: RunnableLambda — any Python function as a Runnable")
print("=" * 60)

# ANY Python function can become a Runnable with RunnableLambda
# This is how you add custom logic to your chains

def fetch_fake_context(question: str) -> str:
    """Simulate fetching context from a database."""
    # In real life, this would query a vector store or database
    contexts = {
        "python": "Python is a high-level programming language created by Guido van Rossum.",
        "rust": "Rust is a systems programming language focused on safety and performance.",
    }
    # Simple keyword matching
    for key, value in contexts.items():
        if key in question.lower():
            return value
    return "No specific context found."

def format_with_context(inputs: dict) -> dict:
    """Add context to the inputs dict."""
    question = inputs["question"]
    context = fetch_fake_context(question)      # Our custom function
    return {
        "question": question,
        "context": context,
    }

# Wrap the function as a Runnable with RunnableLambda
format_step = RunnableLambda(format_with_context)

# Now it works in a chain!
rag_chain = (
    format_step      # dict with 'question' → dict with 'question' + 'context'
    | ChatPromptTemplate.from_template(
        "Use this context: {context}\nAnswer: {question}"
    )
    | llm
    | parser
)

result = rag_chain.invoke({"question": "Tell me about Python."})
print(f"RAG result: {result[:200]}")


# ── LESSON 4: RunnableParallel — Multiple Branches ────────────────────────────
print("\n" + "=" * 60)
print("LESSON 4: RunnableParallel — run branches simultaneously")
print("=" * 60)

# RunnableParallel runs MULTIPLE chains on the SAME input, concurrently
# Returns a dict where keys = branch names, values = branch outputs

# Create specialized prompts for different analyses
sentiment_chain = (
    ChatPromptTemplate.from_template(
        "Rate the sentiment of this text as positive/negative/neutral: {text}"
    ) | llm | parser
)

summary_chain = (
    ChatPromptTemplate.from_template(
        "Summarize this in 10 words: {text}"
    ) | llm | parser
)

keywords_chain = (
    ChatPromptTemplate.from_template(
        "List 3 keywords from: {text}. Just the words, comma separated."
    ) | llm | parser
)

# Run all 3 simultaneously on the same input
parallel_analysis = RunnableParallel(
    sentiment=sentiment_chain,    # Key name → chain to run
    summary=summary_chain,
    keywords=keywords_chain,
)

sample_text = "The new iPhone is incredible but way too expensive for most people."
results = parallel_analysis.invoke({"text": sample_text})

print(f"Sentiment: {results['sentiment']}")
print(f"Summary: {results['summary']}")
print(f"Keywords: {results['keywords']}")

# 💡 ALTERNATE SYNTAX using dict shorthand (same thing, cleaner)
parallel_v2 = {
    "sentiment": sentiment_chain,
    "summary": summary_chain,
    "keywords": keywords_chain,
}   # LangChain automatically wraps dict in RunnableParallel


# ── LESSON 5: itemgetter — Picking Dict Keys ──────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 5: itemgetter — clean dict key selection")
print("=" * 60)

# When your chain gets a dict, use itemgetter to pull specific keys
# This avoids lambda x: x["key"] everywhere

from operator import itemgetter

# A chain that takes a dict with multiple keys
question_answer_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are an expert in {domain}."),
        ("human", "{question}"),
    ])
    | llm
    | parser
)

# itemgetter("key") is equivalent to lambda x: x["key"]
# but cleaner and works everywhere a Runnable is expected
structured_chain = (
    {
        "domain": itemgetter("domain"),      # Pull "domain" from input dict
        "question": itemgetter("question"),  # Pull "question" from input dict
    }
    | question_answer_chain
)

result = structured_chain.invoke({
    "domain": "machine learning",
    "question": "What is overfitting?",
    "other_stuff": "ignored",           # Extra keys are ignored!
})
print(f"Result: {result[:200]}")


# ── LESSON 6: RunnableBranch — Conditional Logic ──────────────────────────────
print("\n" + "=" * 60)
print("LESSON 6: RunnableBranch — routing based on conditions")
print("=" * 60)

# RunnableBranch routes input to different chains based on conditions
# Syntax: RunnableBranch( (condition1, chain1), (condition2, chain2), default )

def is_coding_question(x: dict) -> bool:
    """Check if the question is about coding."""
    coding_words = ["code", "function", "class", "python", "javascript", "bug", "error"]
    return any(word in x["question"].lower() for word in coding_words)

def is_math_question(x: dict) -> bool:
    """Check if the question is mathematical."""
    math_words = ["calculate", "compute", "solve", "equation", "derivative", "integral"]
    return any(word in x["question"].lower() for word in math_words)

# Different chains for different question types
coding_chain = (
    ChatPromptTemplate.from_template(
        "You are a code expert. {question} Provide code example."
    ) | llm | parser
)

math_chain = (
    ChatPromptTemplate.from_template(
        "You are a math tutor. Solve step by step: {question}"
    ) | llm | parser
)

general_chain = (
    ChatPromptTemplate.from_template(
        "Answer this general question: {question}"
    ) | llm | parser
)

# Build the router
router = RunnableBranch(
    (is_coding_question, coding_chain),    # If coding → coding_chain
    (is_math_question, math_chain),        # Elif math → math_chain
    general_chain,                          # Default: general_chain
)

# Test routing
test_questions = [
    "Write a Python function to reverse a string",  # → coding
    "Calculate the derivative of x^2",              # → math
    "What is the capital of France?",               # → general
]

for q in test_questions:
    result = router.invoke({"question": q})
    print(f"Q: {q[:40]}... → {result[:80]}...")


# ── LESSON 7: Fallback Chains ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 7: Fallback chains — handling errors gracefully")
print("=" * 60)

# .with_fallbacks() adds backup chains if the primary fails
# Essential for production reliability

primary_llm = ChatGroq(model="llama3-70b-8192", temperature=0)  # Bigger, might timeout
fallback_llm = ChatGroq(model="llama3-8b-8192", temperature=0)  # Smaller, more reliable

primary_chain = (
    ChatPromptTemplate.from_template("Explain {concept} deeply.")
    | primary_llm
    | parser
)

fallback_chain = (
    ChatPromptTemplate.from_template("Briefly explain {concept}.")
    | fallback_llm
    | parser
)

# If primary_chain fails (timeout, rate limit, etc.), fallback_chain runs
reliable_chain = primary_chain.with_fallbacks([fallback_chain])
result = reliable_chain.invoke({"concept": "neural networks"})
print(f"Reliable result: {result[:150]}...")


# ── KEY TAKEAWAYS ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("KEY TAKEAWAYS FROM PROJECT 3:")
print("=" * 60)
print("""
1. prompt | llm | parser   is the standard chain pattern
2. RunnablePassthrough.assign() adds keys to a dict without removing others
3. RunnableLambda wraps ANY Python function into a Runnable
4. RunnableParallel (or dict) runs branches concurrently, returns dict
5. itemgetter("key") picks dict keys cleanly (better than lambda)
6. RunnableBranch routes to different chains based on conditions
7. .with_fallbacks([backup]) adds error recovery
8. Chains are LAZY — they don't run until .invoke() is called
""")
