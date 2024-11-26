import os
import openai
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.pydantic_v1 import BaseModel as LCBaseModel, Field
from langchain_core.tools import StructuredTool, Tool
from langchain_openai import ChatOpenAI
from tools.rag_tool import add_file_to_knowledge_base, query_knowledge_base
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
# FastAPI app
app = FastAPI(debug=True)

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Agent tools
tools = [
    Tool(
        name="QueryKnowledgeBase",
        func=query_knowledge_base,
        description="Query the knowledge base to retrieve answers.",
    ),
]

# Create the agent
prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

# Create the agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# API endpoint for chat
class UserQuery(BaseModel):
    query: str

@app.post("/chat")
def chat_endpoint(user_query: UserQuery):
    try:
        response = agent_executor.invoke({"input": user_query.query})
        if response and "output" in response:
            print(f"response is  {response} to knowledge base...")
            return {"response": response["output"]}
        else:
            return {"error": "Agent execution failed or returned no output."}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}


# API endpoint for file upload
@app.post("/upload")
def upload_file(file: UploadFile):
    print('hello upload')
    file_path = f"uploaded_files/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    try:
        message = add_file_to_knowledge_base(file_path)
        return {"message": message}
    except Exception as e:
        return {"error": str(e)}