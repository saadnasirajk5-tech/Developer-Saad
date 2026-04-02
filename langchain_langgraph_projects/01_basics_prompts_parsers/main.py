import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Load environment variables (like GEMINI_API_KEY) from .env file
# We are assuming .env is in the parent directory or the current directory
load_dotenv(dotenv_path='../.env') # Tries parent first
load_dotenv() # Fallback to current dir

# Check if the API key is set
if not os.environ.get("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY is not set in the environment.")
    print("Please create a .env file in the root folder based on .env.example and add your API key.")
    exit(1)

# Step 1: Initialize the Model
# We use ChatGoogleGenerativeAI to access the Google Gemini API.
# gemini-1.5-flash is fast, reliable, and has a generous free tier.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3, # Lower temperature means less creative, more deterministic output
)

# Step 2: Define the Output Schema using Pydantic
# Pydantic is widely used with LangChain. It helps us enforce a specific JSON structure 
# from the LLM, making the output predictable and easy to integrate into regular code.
class SummaryOutput(BaseModel):
    summary: str = Field(description="A brief 1-sentence summary of the text.")
    key_points: list[str] = Field(description="A list of 3 key points extracted from the text.")
    sentiment: str = Field(description="The overall sentiment of the text (positive, negative, or neutral).")

# Step 3: Initialize the Output Parser
# This parser takes our Pydantic class and will automatically generate instructions for the LLM
# and parse the resulting text into a Python dictionary.
parser = JsonOutputParser(pydantic_object=SummaryOutput)

# Step 4: Create a Prompt Template
# Templates allow us to reuse prompts with different input variables.
template_string = """
Analyze the following text and extract information according to the rules below.

{format_instructions}

Text to analyze:
{text}
"""

# We bind the parser's instructions into the prompt template dynamically
prompt = PromptTemplate(
    template=template_string,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Step 5: Chain them together using LCEL (LangChain Expression Language)
# The pipe operator (|) sequences operations:
# 1. Provide variables to `prompt` to build the final string.
# 2. Pass string to `llm` to get a response message.
# 3. Pass message to `parser` to parse JSON out of it.
chain = prompt | llm | parser

# Step 6: Execute the Chain
if __name__ == "__main__":
    sample_text = """
    LangChain is a framework for developing applications powered by language models. 
    It enables applications that are context-aware and reason. 
    The core modules include Models, Prompts, Memory, Indexes, Chains, and Agents. 
    LangGraph is an extension of LangChain aimed at building robust, stateful multi-actor applications with LLMs.
    Learning these tools can be highly rewarding, but the learning curve can be steep initially.
    """
    
    print("🤖 Processing text using Gemini and LangChain...")
    try:
        # We invoke the chain and pass the dictionary of input variables
        result = chain.invoke({"text": sample_text})
        
        # Because we used a JsonOutputParser, the result is natively a Python dictionary!
        print("\n--- ✅ Result (Parsed Python Dictionary) ---")
        import json
        print(json.dumps(result, indent=2))
        
        print("\n--- 🧠 Why we built this ---")
        print("Raw LLM outputs are just plain text strings, which are hard for standard")
        print("software to work with. By combining a PromptTemplate and an OutputParser,")
        print("we force Gemini to return structured JSON. The chain automatically parsed")
        print("that JSON into a Python dictionary so you can access fields like `result['sentiment']`")
        print("predictably. This is the foundation of building robust LLM applications!")

        # Proof that it's a dict:
        print(f"\nProof: Sentiment detected as -> {result['sentiment']}")

    except Exception as e:
        print(f"An error occurred: {e}")
