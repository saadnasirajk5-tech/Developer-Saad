"""
================================================================================
PROJECT 5: Basic RAG — Retrieval-Augmented Generation
================================================================================
WHAT YOU LEARN:
  - What RAG is and why it's the most important LLM pattern
  - Document loaders: loading text, PDFs, web pages
  - Text splitters: chunking documents intelligently
  - Embeddings: turning text into vectors (FREE with HuggingFace)
  - Vector stores: storing and searching vectors (FAISS, Chroma)
  - Retrievers: the interface for fetching relevant chunks
  - Complete RAG chain: load → split → embed → store → retrieve → answer

WHAT IS RAG?
  Problem: LLMs only know what was in their training data.
           They can't answer questions about YOUR documents.
  
  Solution: 
  1. Index your documents into a vector store
  2. When user asks a question:
     a. Find the most relevant document chunks (retrieval)
     b. Add those chunks as context to the prompt (augmentation)
     c. LLM generates an answer using that context (generation)
  
  Result: LLM can answer questions about ANY document you give it!

SECRET TIP: The quality of your chunking strategy matters MORE than
            your choice of LLM model. Bad chunks = bad answers.
================================================================================
"""

import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Document loaders — turn files/web pages into LangChain Documents
from langchain_community.document_loaders import (
    TextLoader,              # Load .txt files
    # PyPDFLoader,           # Load PDF files (needs pypdf)
    # WebBaseLoader,         # Load web pages (needs bs4)
    # CSVLoader,             # Load CSV files
)

# Text splitters — chunk documents into pieces
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,   # Best general-purpose splitter
    CharacterTextSplitter,            # Simple char-based splitting
    # MarkdownHeaderTextSplitter,     # Splits at markdown headers
    # TokenTextSplitter,              # Splits by token count exactly
)

# Embeddings — convert text to vectors (FREE! Runs locally)
from langchain_huggingface import HuggingFaceEmbeddings

# Vector stores — store and search embedding vectors
from langchain_community.vectorstores import FAISS    # Facebook's fast library

load_dotenv()
llm = ChatGroq(model="llama3-8b-8192", temperature=0)
parser = StrOutputParser()


# ── STEP 1: Create Sample Documents ──────────────────────────────────────────
print("=" * 60)
print("STEP 1: Creating sample documents for RAG demo")
print("=" * 60)

# Create a temporary text file to demo document loading
# In real projects, these would be your actual documents
sample_text = """
LangChain Framework Overview

LangChain is a framework for developing applications powered by large language models (LLMs).
It was created by Harrison Chase and released in 2022.
LangChain provides tools for chaining together LLM calls, managing prompts, and integrating
with external data sources and APIs.

Key LangChain Components:
1. LLMs and Chat Models: Interfaces to AI models from OpenAI, Anthropic, Groq, and others.
2. Prompt Templates: Reusable templates for structuring inputs to models.
3. Chains (LCEL): Composable pipelines using the pipe operator.
4. Memory: Systems for persisting conversation history across turns.
5. Agents: LLMs that decide what actions to take using tools.
6. Tools: Functions that agents can call (search, calculator, APIs).

LangChain Expression Language (LCEL):
LCEL is the modern way to compose LangChain components.
It uses the pipe operator | to connect components.
Every component implements the Runnable interface with invoke/stream/batch.

Vector Stores and RAG:
RAG (Retrieval-Augmented Generation) is a technique to give LLMs access to external knowledge.
Documents are split into chunks, converted to embeddings, and stored in vector databases.
When a question is asked, relevant chunks are retrieved and added to the prompt context.
Popular vector stores include FAISS, Chroma, Pinecone, and Weaviate.

LangGraph:
LangGraph is built on top of LangChain for building stateful, multi-actor applications.
It represents agent logic as a directed graph with nodes and edges.
Nodes are Python functions that transform state.
Edges determine which node to visit next.
LangGraph supports cycles, human-in-the-loop, and parallel execution.
"""

# Write sample text to a file
os.makedirs("./temp_docs", exist_ok=True)       # Create temp directory
with open("./temp_docs/langchain_overview.txt", "w") as f:
    f.write(sample_text)
print("✅ Sample document created")


# ── STEP 2: Load Documents ────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Loading documents with TextLoader")
print("=" * 60)

# TextLoader loads a text file as a LangChain Document object
loader = TextLoader(
    "./temp_docs/langchain_overview.txt",
    encoding="utf-8"    # Specify encoding to avoid issues
)

# .load() returns a LIST of Document objects
# Each Document has: .page_content (text) and .metadata (dict)
raw_docs = loader.load()

print(f"Loaded {len(raw_docs)} documents")           # Usually 1 for .txt
print(f"Type: {type(raw_docs[0])}")                  # <class 'langchain_core.documents.base.Document'>
print(f"Content preview: {raw_docs[0].page_content[:100]}...")
print(f"Metadata: {raw_docs[0].metadata}")           # {'source': 'path/to/file.txt'}

# 💡 TIP: For PDFs, use PyPDFLoader — it creates one Document per page
# for pdf_doc in raw_docs:
#     print(f"Page {pdf_doc.metadata['page']}: {pdf_doc.page_content[:50]}")


# ── STEP 3: Split Documents into Chunks ───────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3: Splitting documents into chunks")
print("=" * 60)

# RecursiveCharacterTextSplitter is the best general-purpose splitter
# It tries to split on: paragraphs → sentences → words → characters
# This keeps semantically related content together

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,         # Target size of each chunk in CHARACTERS (not tokens!)
                            # 500 chars ≈ 125 tokens ≈ good for most retrievers
    chunk_overlap=50,       # Overlap between chunks prevents losing context at boundaries
                            # Rule of thumb: 10% of chunk_size
    length_function=len,    # How to measure length (can use token counter)
    separators=[            # Try to split on these, in order
        "\n\n",             # First try paragraph breaks (best)
        "\n",               # Then line breaks
        ". ",               # Then sentence ends
        " ",                # Then words
        "",                 # Last resort: any character
    ]
)

# Split the loaded documents
chunks = splitter.split_documents(raw_docs)

print(f"Original: 1 document → Split into: {len(chunks)} chunks")
print(f"\nChunk 0 preview:")
print(f"  Content: {chunks[0].page_content[:150]}...")
print(f"  Length: {len(chunks[0].page_content)} chars")
print(f"  Metadata: {chunks[0].metadata}")      # Metadata carried over from parent!

# 💡 SECRET TIP: Metadata is CRUCIAL for filtering later
# Add metadata to track source, date, author, etc.
for i, chunk in enumerate(chunks):
    chunk.metadata["chunk_id"] = i              # Add chunk index
    chunk.metadata["source_type"] = "overview"  # Add document type

print(f"\nAll chunks sizes: {[len(c.page_content) for c in chunks]}")


# ── STEP 4: Create Embeddings ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4: Creating embeddings (FREE, local HuggingFace model)")
print("=" * 60)

# Embeddings turn text into vectors of numbers
# Similar text → similar vectors (high cosine similarity)
# This is how "semantic search" works

# HuggingFaceEmbeddings uses local models — no API key needed!
# First run downloads the model (~90MB), then it's cached
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",   # 384-dim, fast, high quality
                                             # Other options:
                                             # "all-MiniLM-L6-v2" (384-dim, very fast)
                                             # "BAAI/bge-large-en-v1.5" (1024-dim, better)
    model_kwargs={"device": "cpu"},         # Use CPU (change to "cuda" for GPU)
    encode_kwargs={"normalize_embeddings": True},  # L2 normalize for cosine similarity
)

# Test the embedding
test_text = "What is LangChain?"
embedding = embedding_model.embed_query(test_text)   # embed_query for single texts

print(f"Text: '{test_text}'")
print(f"Embedding dimensions: {len(embedding)}")      # 384 for bge-small
print(f"First 5 values: {embedding[:5]}")             # Floats between -1 and 1
print(f"Embedding is a {type(embedding)}")            # list of floats

# Two similar texts should have similar embeddings
emb1 = embedding_model.embed_query("What is LangChain?")
emb2 = embedding_model.embed_query("Tell me about LangChain framework")
emb3 = embedding_model.embed_query("What is a pizza?")

import numpy as np
def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"\nSimilarity (LangChain vs LangChain): {cosine_similarity(emb1, emb2):.3f}")  # High!
print(f"Similarity (LangChain vs Pizza):     {cosine_similarity(emb1, emb3):.3f}")   # Low!


# ── STEP 5: Create Vector Store ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5: Indexing chunks into FAISS vector store")
print("=" * 60)

# FAISS.from_documents() does THREE things:
# 1. Takes all chunk texts
# 2. Calls embedding_model to convert each chunk to a vector
# 3. Stores vectors + original text in FAISS index
vectorstore = FAISS.from_documents(
    documents=chunks,                   # The text chunks to index
    embedding=embedding_model,          # How to create vectors
)

print(f"✅ FAISS index created with {vectorstore.index.ntotal} vectors")

# Save to disk for reuse (so you don't re-embed every time!)
vectorstore.save_local("./temp_docs/faiss_index")
print("💾 Index saved to disk")

# Load from disk
loaded_store = FAISS.load_local(
    "./temp_docs/faiss_index",
    embeddings=embedding_model,         # Must use same embedding model!
    allow_dangerous_deserialization=True  # Required flag for loading
)
print(f"📂 Index loaded from disk: {loaded_store.index.ntotal} vectors")

# Similarity search — find chunks most similar to a query
query = "How does LCEL work?"
similar_docs = vectorstore.similarity_search(
    query,
    k=3    # Return top 3 most similar chunks
)
print(f"\nQuery: '{query}'")
print(f"Top 3 similar chunks:")
for i, doc in enumerate(similar_docs):
    print(f"  [{i+1}] Score preview: {doc.page_content[:100]}...")

# With scores (lower = more similar in FAISS L2 distance)
docs_with_scores = vectorstore.similarity_search_with_score(query, k=3)
for doc, score in docs_with_scores:
    print(f"  Score: {score:.4f} | {doc.page_content[:80]}...")


# ── STEP 6: Create a Retriever ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 6: Creating a retriever (the RAG interface)")
print("=" * 60)

# A Retriever is a Runnable that:
#   Input: string (the query)
#   Output: List[Document] (relevant chunks)

retriever = vectorstore.as_retriever(
    search_type="similarity",    # Options: "similarity", "mmr", "similarity_score_threshold"
                                  # "mmr" = Maximal Marginal Relevance (diverse results)
    search_kwargs={
        "k": 4,                  # Number of chunks to retrieve
        # "score_threshold": 0.5,  # Only return if similarity > threshold (for "similarity_score_threshold")
        # "filter": {"source_type": "overview"},  # Filter by metadata!
    }
)

# Test retriever directly
results = retriever.invoke("What is LangGraph?")
print(f"Query: 'What is LangGraph?'")
print(f"Retrieved {len(results)} chunks:")
for r in results:
    print(f"  - {r.page_content[:80]}...")


# ── STEP 7: Build the Complete RAG Chain ──────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 7: Building and running the complete RAG chain")
print("=" * 60)

# RAG Prompt — includes context from retrieved chunks
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer questions based ONLY on the 
provided context. If the answer is not in the context, say "I don't have that information."

Context:
{context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    """
    Convert a list of Document objects into a single string.
    This is the 'context' that gets inserted into the prompt.
    """
    return "\n\n---\n\n".join([
        f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    ])

# The complete RAG chain
rag_chain = (
    {
        # Retrieve relevant chunks and format them as context
        "context": retriever | format_docs,    # query → docs → formatted string
        
        # Pass the question through unchanged
        "question": RunnablePassthrough(),     # question → question
    }
    | rag_prompt           # Insert context + question into prompt
    | llm                  # Generate answer
    | parser               # Convert AIMessage → string
)

# Ask questions!
questions = [
    "What is LangChain and who created it?",
    "What is LCEL and how does it work?",
    "What is LangGraph?",
    "What are the main components of LangChain?",
    "What is the capital of France?",  # Out of context — should say "I don't have that"
]

for q in questions:
    print(f"\n❓ Q: {q}")
    answer = rag_chain.invoke(q)    # Note: pass string directly (retriever handles it)
    print(f"💬 A: {answer[:200]}...")


# ── KEY TAKEAWAYS ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("KEY TAKEAWAYS FROM PROJECT 5:")
print("=" * 60)
print("""
RAG PIPELINE:
  Load → Split → Embed → Store → Retrieve → Augment → Generate

Key decisions:
1. Chunk size matters most — 500 chars is a good starting point
2. Chunk overlap prevents losing context at boundaries (use 10%)
3. HuggingFaceEmbeddings = FREE and works great
4. FAISS = fast, local, save/load from disk
5. retriever = vectorstore.as_retriever(search_type, search_kwargs)
6. format_docs() converts List[Document] → string for the prompt
7. RunnablePassthrough() passes the question unchanged through the chain
8. Add metadata to chunks for filtering (very powerful!)
""")

# Cleanup
import shutil
shutil.rmtree("./temp_docs", ignore_errors=True)
