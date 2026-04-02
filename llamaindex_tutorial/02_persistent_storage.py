import os
import os.path
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

load_dotenv()

PERSIST_DIR = "./storage"

def main():
    if not os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY") == "your-api-key-here":
        print("Please set your GOOGLE_API_KEY in the .env file!")
        return

    # Configure LlamaIndex to use Gemini
    Settings.llm = Gemini(model="models/gemini-1.5-flash")
    Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

    if not os.path.exists(PERSIST_DIR):
        print("Storage not found. Loading documents and building the index from scratch...")
        documents = SimpleDirectoryReader("data").load_data()
        index = VectorStoreIndex.from_documents(documents)
        
        print("Saving index to disk...")
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        print("Storage found! Reloading the existing index off the disk...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        print("Index loaded from disk successfully!")

    query_engine = index.as_query_engine()
    
    question = "What is Retrieval-Augmented Generation?"
    print(f"\nQ: {question}")
    response = query_engine.query(question)
    print(f"A: {response}")

if __name__ == "__main__":
    main()
