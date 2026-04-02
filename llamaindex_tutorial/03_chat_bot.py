import os
from dotenv import load_dotenv

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

load_dotenv()

def main():
    if not os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY") == "your-api-key-here":
        print("Please set your GOOGLE_API_KEY in the .env file!")
        return

    # Configure LlamaIndex to use Gemini
    Settings.llm = Gemini(model="models/gemini-1.5-flash")
    Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

    print("Welcome to the LlamaIndex Chatbot Tutorial (Using Gemini)!")
    print("Loading data and configuring index...")

    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    
    chat_engine = index.as_chat_engine()
    
    print("Chat engine ready! (Type 'quit' or 'exit' to stop)")
    print("Try asking what LlamaIndex does, and then follow up with 'what are its core components?'")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break
            
        response = chat_engine.chat(user_input)
        print(f"\nAI: {response}")

if __name__ == "__main__":
    main()
