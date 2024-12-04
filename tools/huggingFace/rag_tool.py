from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader, CSVLoader
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the embedding model
embedding_model = SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the HuggingFace pipeline for LLM
llm_pipeline = pipeline(
    "text-generation",
    model="EleutherAI/gpt-neo-2.7B",
    num_return_sequences=1,
    temperature=0.7,
    max_length=1024,  # Increase max_length to handle longer inputs
    truncation=True
)
llm = HuggingFacePipeline(pipeline=llm_pipeline)

# Function to process the file and generate text chunks
def process_file(file_path: str):
    """
    Process a file and return its text.
    Supports PDF, Word (.docx), and CSV files.
    """
    print(f"Processing file: {file_path}")
    
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        print("PDF file detected, using PyPDFLoader")
    elif file_path.endswith(".docx"):
        loader = UnstructuredFileLoader(file_path)
        print("DOCX file detected, using UnstructuredFileLoader")
    elif file_path.endswith(".csv"):
        loader = CSVLoader(file_path)
        print("CSV file detected, using CSVLoader")
    else:
        raise ValueError(f"Unsupported file format!")

    documents = loader.load()
    if not documents:
        print(f"No documents loaded from the file!")
    else:
        print(f"Documents loaded: {len(documents)}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    if not texts:
        print(f"No text chunks generated!")
    else:
        print(f"Text splitting completed. Sample text")

    return texts

# Function to add file to the knowledge base
def add_file_to_knowledge_base(file_path: str):
    """
    Add a file's content to the vector store knowledge base.
    """
    print(f"Adding file {file_path} to knowledge base...")
    texts = process_file(file_path)
    global vector_store

    # Initialize the Chroma vector store with persistence
    vector_store = Chroma.from_documents(
        documents=texts,
        embedding=embedding_model,
        persist_directory="knowledge_base"  # Specify persistence directory
    )
    print(f"Vector store created and documents added!")
    print(f"Vector store now has {len(texts)} documents.")
    return f"File {os.path.basename(file_path)} added to the knowledge base!"

# Function to query the knowledge base
def query_knowledge_base(query: str) -> str:
    """
    Query the knowledge base and return an answer.
    """
    print(f"Querying knowledge base with: {query}")

    # Check if the vector store is initialized
    if vector_store is None:
        print(f"Knowledge base is empty. Please upload files first.")
        return "Knowledge base is empty. Please upload files first."

    retriever = vector_store.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,  # Pass the LLM instance here
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
    )

    print(f"Retrieving answer...")
    response = qa_chain.invoke({
    "query": query,
    "max_new_tokens": 100,  # Define how many new tokens to generate
})
    print(f"Answer retrieved: {response}")
    return response

# Define the RAG tool
def query_tool(query: str) -> str:
    """Tool function to query the knowledge base."""
    return query_knowledge_base(query)

# Test with file upload and query
if __name__ == "__main__":
    file_path = "uploaded_files/sample-pdf-a4-size-65kB.pdf"  # Replace with your file path
    print(add_file_to_knowledge_base(file_path))  # Add the file to the knowledge base

    # Example query
    query = "What is the content of the uploaded document?"
    print(query_knowledge_base(query))  # Query the knowledge base after file upload
