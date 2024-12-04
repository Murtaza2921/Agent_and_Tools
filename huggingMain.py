import os
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from langchain_core.tools import Tool
from transformers import pipeline
from dotenv import load_dotenv
from tools.huggingFace.rag_tool import add_file_to_knowledge_base, query_knowledge_base

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(debug=True)

# Initialize the Hugging Face model (text generation pipeline)
llm_pipeline = pipeline("text-generation", model="EleutherAI/gpt-neo-2.7B", num_return_sequences=1, temperature=0.7)

# Define tools for agent interaction
tools = [
    Tool(
        name="QueryKnowledgeBase",
        func=query_knowledge_base,
        description="Query the knowledge base to retrieve answers.",
    ),
]

# Define a custom agent for managing tool calling and response generation
class CustomAgent:
    def __init__(self, llm_pipeline, tools):
        self.llm_pipeline = llm_pipeline
        self.tools = {tool.name: tool for tool in tools}

    def invoke(self, inputs):
        """
        Handle input and invoke the appropriate tool or generate a response.
        """
        question = inputs["input"]
        
        # Check if the query is related to the knowledge base
        if "knowledge base" in question.lower() or "file" in question.lower():
            # Explicitly call the RAG tool
            response = self.tools["QueryKnowledgeBase"].func(question)
            return {"output": response}
        
        # If not related to the knowledge base, generate response with the LLM
        llm_output = self.llm_pipeline(question, max_length=200, num_return_sequences=1)[0]["generated_text"]
        return {"output": llm_output}

# Initialize the custom agent
agent = CustomAgent(llm_pipeline, tools)

# Define API endpoint for chat
class UserQuery(BaseModel):
    query: str

@app.post("/chat")
def chat_endpoint(user_query: UserQuery):
    """
    Endpoint for querying the agent.
    """
    try:
        response = agent.invoke({"input": user_query.query})
        if response and "output" in response:
            print(f"Response: {response['output']}")
            return {"response": response["output"]}
        else:
            return {"error": "Agent execution failed or returned no output."}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}

# Define API endpoint for file upload
@app.post("/upload")
def upload_file(file: UploadFile):
    """
    Endpoint for uploading files to the knowledge base.
    """
    print('File upload received...')
    file_path = f"uploaded_files/{file.filename}"
    os.makedirs("uploaded_files", exist_ok=True)  # Ensure the directory exists
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    try:
        message = add_file_to_knowledge_base(file_path)
        print(f"File successfully added: {message}")
        return {"message": message}
    except Exception as e:
        print(f"Error during file processing: {e}")
        return {"error": str(e)}

# Run this if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
