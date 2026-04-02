import os
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.documents import Document

load_dotenv(dotenv_path='../.env')

def main():
    print("🚀 Starting Advanced Conversational RAG")
    # 1. Setup mock data & Chroma (persistent)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Let's mock having some company data
    docs = [
        Document(page_content="Our company is called NexaTech. We build AI software."),
        Document(page_content="NexaTech's CEO is Jane Doe. She founded the company in 2021."),
        Document(page_content="Our flagship product is called 'NexaMind', an enterprise Chatbot."),
        Document(page_content="NexaMind costs $100/month per user.")
    ]
    
    # Notice we save it to disk this time using persist_directory
    vectorstore = Chroma.from_documents(
        documents=docs, 
        embedding=embeddings, 
        persist_directory="./chroma_db"
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # 2. Handle Conversational History (History-Aware Retriever)
    # Why? If user says "What is its price?", the word "its" is ambiguous.
    # We need to re-write the query based on chat history to "What is the price of NexaMind?"
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"), # This is where old messages are injected
        ("human", "{input}"),
    ])
    
    # This retriever first asks the LLM to rewrite the query, then searches the DB
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 3. Create the Question Answering Chain
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Keep the answer concise.\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # This chain handles stuffing the documents into the prompt
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 4. Tie it all together
    # This brings together the history-aware retriever and the QA chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # 5. Simulate a Conversation
    chat_history = []
    
    print("\n--- Turn 1 ---")
    question1 = "What is the flagship product?"
    print(f"User: {question1}")
    res1 = rag_chain.invoke({"input": question1, "chat_history": chat_history})
    print(f"AI: {res1['answer']}")
    
    # Update History! This is crucial.
    chat_history.extend([HumanMessage(content=question1), AIMessage(content=res1["answer"])])

    print("\n--- Turn 2 (Testing Memory) ---")
    # The big test: "How much does it cost?". "It" requires memory!
    question2 = "How much does it cost?"
    print(f"User: {question2}")
    res2 = rag_chain.invoke({"input": question2, "chat_history": chat_history})
    print(f"AI: {res2['answer']}")
    
    print("\n--- 🧠 Why we did this ---")
    print("Normal RAG forgets everything from the previous prompt.")
    print("By implementing a history-aware retriever, we instructed the LLM to look at previous")
    print("context (like 'flagship product' -> 'NexaMind') before doing a vector search for 'cost'.")
    print("This allows for natural, multi-turn conversations with your documents!")

if __name__ == "__main__":
    main()
