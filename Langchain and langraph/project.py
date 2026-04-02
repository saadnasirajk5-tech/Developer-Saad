"""
================================================================================
PROJECT 1: Hello World — Your First LangChain LLM Call
================================================================================
WHAT YOU LEARN:
  - How to connect to an LLM (Groq - FREE)
  - The .invoke() method — the most basic LangChain operation
  - HumanMessage vs SystemMessage vs AIMessage
  - Synchronous vs Asynchronous calls
  - Streaming tokens as they arrive

CORE CONCEPT:
  LangChain's fundamental abstraction is the "Runnable" interface.
  Every LLM, chain, and prompt is a Runnable.
  Runnables have 3 key methods:
    .invoke()    → get one complete response
    .stream()    → get tokens as they arrive
    .batch()     → process multiple inputs at once

FREE API: Groq gives you llama3-8b for free at console.groq.com
================================================================================
"""

# ── Imports ───────────────────────────────────────────────────────────────────

import os                                           # Read environment variables
from dotenv import load_dotenv                      # Load .env file if present

# LangChain message types — these represent chat history entries
from langchain_core.messages import (
    HumanMessage,    # A message from the human/user
    SystemMessage,   # Instructions that set the AI's behavior
    AIMessage,       # A response from the AI
)

# Groq is our FREE LLM provider
# Install: pip install langchain-groq
from langchain_groq import ChatGroq

# ── Setup ─────────────────────────────────────────────────────────────────────

load_dotenv()   # Loads GROQ_API_KEY from .env file if it exists
                # If not in .env, it reads from environment variables

# ── Initialize the LLM ────────────────────────────────────────────────────────

llm = ChatGroq(
    model="llama3-8b-8192",   # Model name on Groq. FREE options:
                               #   llama3-8b-8192     (fast, smart)
                               #   llama3-70b-8192    (smarter, slower)
                               #   mixtral-8x7b-32768 (32k context!)
                               #   gemma2-9b-it       (Google's model)
    temperature=0,             # 0 = deterministic (same answer every time)
                               # 1 = creative/random
                               # For factual tasks: use 0
                               # For creative tasks: use 0.7-1.0
    max_tokens=1024,           # Maximum tokens in the response
                               # 1 token ≈ 0.75 words in English
)

# ── LESSON 1: Basic Invoke ─────────────────────────────────────────────────────
print("=" * 60)
print("LESSON 1: Basic .invoke() with a string")
print("=" * 60)

# The simplest possible LangChain call
# .invoke() sends the input and waits for the complete response
response = llm.invoke("What is LangChain? Answer in one sentence.")

# response is an AIMessage object, not a plain string
print(f"Type: {type(response)}")          # <class 'langchain_core.messages.ai.AIMessage'>
print(f"Content: {response.content}")     # The actual text response
print(f"Model: {response.response_metadata.get('model_name', 'N/A')}")
# TIP: response_metadata has token usage, model name, finish reason


# ── LESSON 2: System + Human Messages ─────────────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 2: Using System + Human messages")
print("=" * 60)

# SystemMessage sets the "persona" or behavior of the AI
# HumanMessage is the user's actual question
# IMPORTANT: The list ORDER matters! System first, then Human

messages = [
    SystemMessage(
        content="You are a Python expert who explains concepts simply. "
                "Always include a tiny code example."
    ),
    HumanMessage(
        content="What is a decorator in Python?"
    ),
]

response = llm.invoke(messages)     # Pass list of messages instead of string
print(response.content)

# 💡 SECRET TIP: You can also add past AI messages to create conversation history
# This is manual memory — you maintain the list yourself
conversation = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="My name is Alex."),
    AIMessage(content="Hi Alex! Nice to meet you."),   # Previous AI response
    HumanMessage(content="What is my name?"),           # Should remember "Alex"
]
response = llm.invoke(conversation)
print(f"\nMemory test: {response.content}")  # Should say "Alex"


# ── LESSON 3: Streaming ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 3: Streaming responses token by token")
print("=" * 60)

# .stream() is a generator — yields chunks as the LLM generates them
# This feels faster to users because they see output immediately
# Perfect for chatbots and interactive applications

print("Streaming: ", end="", flush=True)    # flush=True ensures immediate print

for chunk in llm.stream("Tell me a very short joke."):
    # chunk is an AIMessageChunk with a .content attribute
    print(chunk.content, end="", flush=True)    # Print without newline
print()  # Final newline


# ── LESSON 4: Batch Processing ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("LESSON 4: Batch processing multiple inputs")
print("=" * 60)

# .batch() processes multiple inputs CONCURRENTLY (not sequentially)
# Much faster than calling .invoke() in a loop!
questions = [
    "What is Python?",
    "What is JavaScript?",
    "What is Rust?",
]

# All 3 questions sent concurrently, returns list of responses
responses = llm.batch(questions)

for question, response in zip(questions, responses):
    print(f"Q: {question}")
    print(f"A: {response.content[:100]}...")  # First 100 chars
    print()


# ── LESSON 5: Async (for production web apps) ────────────────────────────────
print("=" * 60)
print("LESSON 5: Async calls (for FastAPI, web servers)")
print("=" * 60)

import asyncio     # Python's async library

async def ask_async():
    """Async calls don't block — essential for web servers."""
    
    # .ainvoke() is the async version of .invoke()
    response = await llm.ainvoke("What is async programming?")
    print(f"Async response: {response.content[:100]}...")
    
    # .astream() is async streaming
    print("\nAsync streaming: ", end="", flush=True)
    async for chunk in llm.astream("Count to 5 slowly"):
        print(chunk.content, end="", flush=True)
    print()

asyncio.run(ask_async())    # Run the async function


# ── KEY TAKEAWAYS ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("KEY TAKEAWAYS FROM PROJECT 1:")
print("=" * 60)
print("""
1. ChatGroq(model=..., temperature=...) initializes the LLM
2. .invoke() = synchronous, returns complete AIMessage
3. .stream() = generator, yields chunks in real-time
4. .batch() = concurrent, processes list of inputs
5. SystemMessage sets behavior, HumanMessage is user input
6. response.content extracts the text from AIMessage
7. Keep a list of messages for manual conversation memory
""")
