import os
from dotenv import load_dotenv

# Document Loading & Splitting
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Embeddings & Vector Store
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# LCEL / chains
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Setup Environment
load_dotenv(dotenv_path='../.env')
if not os.environ.get("GEMINI_API_KEY"):
    print("Error: GEMINI_API_KEY is not set.")
    exit(1)

def main():
    print("🚀 Starting Simple RAG Project")
    
    # 2. Load the Document
    # Documents can be PDFs, Web Pages, text files, etc.
    print("1. Loading document...")
    loader = TextLoader("sample.txt")
    docs = loader.load()
    
    # 3. Split the Document
    # LLMs have context limits so we can't feed them a 1000-page book in one go.
    # We split the text into meaningful 'chunks'.
    print("2. Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,    # max characters per chunk
        chunk_overlap=50   # overlap between chunks to preserve context
    )
    splits = text_splitter.split_documents(docs)
    print(f"   -> Split into {len(splits)} chunks.")

    # 4. Embed and Store chunks
    # An 'Embedding' turns text into an array of numbers (a vector) capturing its meaning.
    # We store these vectors in a Vector Database (like Chroma).
    print("3. Generating embeddings and storing in Chroma...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # We use an in-memory Chroma instance for this simple project
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    # A 'Retriever' is an interface that searches the vector database 
    # to find chunks similar to the user's query.
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # Get top 2 results

    # 5. Define the LLM and Prompt for answering
    print("4. Setting up the RAG chain...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    template = """
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    
    Context: {context}
    
    Question: {question}
    
    Answer:
    """
    custom_prompt = PromptTemplate.from_template(template)

    # 6. Build the LCEL Chain
    # Formatting context: join multiple retrieved documents into a single string
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # The Chain flow:
    # - User provides {"question": "..."}
    # - "context" gets populated by calling the retriever with the question, then formatted
    # - "question" gets passed through as is
    # - The custom_prompt combines both
    # - The llm generates the answer
    # - The output is parsed to a raw string
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_prompt
        | llm
        | StrOutputParser()
    )

    # 7. Ask a question!
    question = "What is a common vulnerability in smart contracts?"
    print(f"\n--- Question: {question} ---")
    
    # Calling the chain
    answer = rag_chain.invoke(question)
    
    print("\n--- ✅ Answer ---")
    print(answer)

    print("\n--- 🧠 Why we did this ---")
    print("This is Pattern #1 for AI applications: Retrieval Augmented Generation (RAG).")
    print("By searching for relevant chunks of our own data (the vector store) and ")
    print("stuffing them into the prompt (the context), we 'teach' the LLM about ")
    print("information it didn't know during training, preventing hallucinations.")

if __name__ == "__main__":
    main()
