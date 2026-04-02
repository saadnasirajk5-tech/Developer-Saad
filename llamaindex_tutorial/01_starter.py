import os
from dotenv import load_dotenv

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# 1. Load environment variables
load_dotenv()

def main():
    if not os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY") == "your-api-key-here":
        print("Please set your GOOGLE_API_KEY in the .env file!")
        return

    # Configure LlamaIndex to use Gemini for both answers and embeddings
    print("Configuring Gemini Models...")
    Settings.llm = Gemini(model="models/gemini-1.5-flash")
    Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

    print("Loading data...")
    documents = SimpleDirectoryReader("data").load_data()
    print(f"Loaded {len(documents)} document(s).")
    
    print("Building the index...")
    index = VectorStoreIndex.from_documents(documents)
    
    print("Index built! Creating query engine...")
    query_engine = index.as_query_engine()
    
    print("\n--- Example Query ---")
    question = "What are the core components of LlamaIndex?"
    print(f"Q: {question}")
    
    response = query_engine.query(question)
    
    print(f"A: {response}")

if __name__ == "__main__":
    main()
