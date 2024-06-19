from langchain.document_loaders import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import TokenTextSplitter,RecursiveCharacterTextSplitter
from datasets import load_dataset
import pandas as pd
import csv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama



def load_and_chunk_documents(csv_file):
    """
    Load documents from CSV file, chunk them, and create FAISS index.

    Args:
    - csv_file (str): Path to the CSV file containing documents.

    Returns:
    - FAISS: FAISS index containing chunked documents.
    """
    # Load documents from CSV
    loader = CSVLoader(file_path=csv_file)
    data = loader.load()

    # Chunk documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=128, chunk_overlap=50)
    chunks = text_splitter.split_documents(data)

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Build FAISS index
    db = FAISS.from_documents(chunks, embeddings)
    return db

def initialize_chatbot():
    """
    Initialize the Ollama model and load and chunk documents.

    Returns:
    - tuple: Tuple containing Ollama model instance and FAISS index.
    """
    # Initialize Ollama model
    llm = Ollama(model="llama3")

    # Load and chunk documents
    csv_file = 'wiki_medical_terms.csv'  # Replace with your CSV file path
    db = load_and_chunk_documents(csv_file)

    return llm, db

def get_chatbot_answer(llm, db, query):
    """
    Retrieve answer from the chatbot for a given query.

    Args:
    - llm (Ollama): Initialized Ollama model instance.
    - db (FAISS): FAISS index containing chunked documents.
    - query (str): Query for which the chatbot should provide an answer.

    Returns:
    - dict: Dictionary containing the chatbot's answer.
    """
    PROMPT_TEMPLATE = """You are a clinical bot that explains medical jargons in simple words. Answer the given questions based on your knowledge and given context.
    {context}
    You are allowed to rephrase the answer based on the context. Explain it so that the normal person can understand it.
    Question: {question}
    """
    PROMPT = PromptTemplate.from_template(PROMPT_TEMPLATE)

    # Retrieve answer using RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=db.as_retriever(k=2),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    result = qa_chain({"query": query})
    return result

def chatbot():
    llm, db = initialize_chatbot()
     # Example query
    query = "What is Acromegaly?"

    # Get chatbot's answer
    result = get_chatbot_answer(llm, db, query)
    print(result['result'])

chatbot()