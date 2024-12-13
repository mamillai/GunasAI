import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from other origins (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict to specific domains)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the input schema for the chat endpoint
class ChatMessage(BaseModel):
    message: str

# Function to query the Ollama Llama3.2 model
def query_ollama(prompt: str) -> str:
    try:
        # Run the Ollama CLI and pass the input prompt
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Check if there are any errors in the CLI output
        if result.returncode != 0:
            raise Exception(f"Error from Ollama: {result.stderr.strip()}")

        # Return the output from Ollama
        return result.stdout.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama Query Failed: {str(e)}")

# Serve the frontend index.html file
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join("static", "index.html"))

# Chat endpoint to interact with the model
@app.post("/api/chat")
async def chat_with_llama(chat: ChatMessage):
    # Call the query function to get the model's response
    reply = query_ollama(chat.message)
    return {"reply": reply}
