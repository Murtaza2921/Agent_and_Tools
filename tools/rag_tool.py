import os
import openai
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from colorama import Fore, Style
from dotenv import load_dotenv

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Directory to store uploaded files
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings()
vector_store = None  # Placeholder for the vector store

def process_file(file_path: str):
    """
    Process a file and return its text.
    Supports PDF, Word (.docx), and CSV files.
    """
    print(f"{CYAN}Processing file: {file_path}{RESET}")
    
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        print(f"{GREEN}PDF file detected, using PyPDFLoader{RESET}")
    elif file_path.endswith(".docx"):
        loader = UnstructuredFileLoader(file_path)
        print(f"{GREEN}DOCX file detected, using UnstructuredFileLoader{RESET}")
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
        print(f"{GREEN}CSV file detected, using CSVLoader{RESET}")
    else:
        raise ValueError(f"{RED}Unsupported file format!{RESET}")

    documents = loader.load()
    
    if not documents:
        print(f"{RED}No documents loaded from the file!{RESET}")
    else:
        print(f"{MAGENTA}Documents loaded: {len(documents)}{RESET}")

    # Split the loaded documents into text chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    if not texts:
        print(f"{RED}No text chunks generated!{RESET}")
    else:
        print(f"{MAGENTA}Text splitting completed. Sample text{RESET}")  # Print a snippet for verification
    
    return texts

def add_file_to_knowledge_base(file_path: str):
    """
    Add a file's content to the vector store knowledge base.
    """
    global vector_store
    print(f"{CYAN}Adding file {file_path} to knowledge base...{RESET}")
    texts = process_file(file_path)

    if vector_store is None:
        vector_store = Chroma.from_documents(texts, embeddings)
        print(f"{GREEN}Vector store created and documents added!{RESET}")
    else:
        vector_store.add_documents(texts)
        print(f"{YELLOW}Documents added to existing knowledge base.{RESET}")

    # Debugging print to check the size of the vector store
    print(f"{MAGENTA}Vector store now has {len(vector_store._collection)} documents.{RESET}")
    return f"{GREEN}File {os.path.basename(file_path)} added to the knowledge base!{RESET}"

def query_knowledge_base(query: str) -> str:
    """
    Query the knowledge base and return an answer.
    """
    print(f"{CYAN}Querying knowledge base with: {query}{RESET}")

    if vector_store is None:
        print(f"{RED}Knowledge base is empty. Please upload files first.{RESET}")
        return "Knowledge base is empty. Please upload files first."

    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
    )

    print(f"{MAGENTA}Retrieving answer...{RESET}")
    response = qa_chain.invoke(query)
    print(f"{BLUE}Answer retrieved: {response}{RESET}")
    return response

# Define the RAG tool
def query_tool(query: str) -> str:
    """Tool function to query the knowledge base."""
    return query_knowledge_base(query)

RAGTool = Tool(
    name="RAGTool",
    func=query_tool,
    description="Retrieves and answers questions based on uploaded files (PDF, Word, CSV).",
)

# Testing the full flow:
if __name__ == "__main__":
    # Example file upload
    file_path = "uploaded_files/06-E-SOC413.pdf"  # Path to your uploaded file
    print(add_file_to_knowledge_base(file_path))  # Add the file to the knowledge base

    # Example query
    query = "Distorted development"
    print(query_knowledge_base(query))  # Query the knowledge base after file upload
