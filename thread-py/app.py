#!/usr/bin/env python3
# filepath: c:\Users\Jaro\Desktop\3rd-devs\thread-py\app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Dict, List, Optional, Any, Union

from openai_service import OpenAIService

# Initialize FastAPI app
app = FastAPI()
openai_service = OpenAIService()
previous_summarization = ""

class Message(BaseModel):
    content: str
    role: str

class ChatRequest(BaseModel):
    message: Message

# Function to generate summarization based on the current turn and previous summarization
async def generate_summarization(user_message: Dict[str, str], assistant_response: Any) -> str:
    global previous_summarization
    
    summarization_prompt = {
        "role": "system",
        "content": f"""Please summarize the following conversation in a concise manner, incorporating the previous summary if available:
<previous_summary>{previous_summarization or "No previous summary"}</previous_summary>
<current_turn> User: {user_message["content"]}\nAssistant: {assistant_response.content} </current_turn>
"""
    }

    response = openai_service.completion(
        [summarization_prompt, {"role": "user", "content": "Please create/update our conversation summary."}],
        "gpt-4o-mini",
        False
    )
    
    return response.choices[0].message.content or "No conversation history"

# Function to create system prompt
def create_system_prompt(summarization: str) -> Dict[str, str]:
    content = "You are Alice, a helpful assistant who speaks using as few words as possible."
    
    if summarization:
        content += f"""

Here is a summary of the conversation so far: 
<conversation_summary>
  {summarization}
</conversation_summary>"""
    
    content += "\n\nLet's chat!"
    
    return {
        "role": "system",
        "content": content
    }

# Chat endpoint POST /api/chat
@app.post("/api/chat")
async def chat(request: Request):
    global previous_summarization
    
    try:
        data = await request.json()
        message = data.get("message")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        system_prompt = create_system_prompt(previous_summarization)
        
        assistant_response = openai_service.completion(
            [system_prompt, message],
            "gpt-4o",
            False
        )
        
        # Generate new summarization
        previous_summarization = await generate_summarization(message, assistant_response.choices[0].message)
        
        return JSONResponse(content=assistant_response)
    
    except Exception as e:
        print(f"Error in OpenAI completion: {e}")
        return JSONResponse(status_code=500, content={"error": "An error occurred while processing your request"})

# Demo endpoint POST /api/demo
@app.post("/api/demo")
async def demo():
    global previous_summarization
    
    demo_messages = [
        {"content": "Hi! I'm Adam", "role": "user"},
        {"content": "How are you?", "role": "user"},
        {"content": "Do you know my name?", "role": "user"}
    ]
    
    assistant_response = None
    
    for message in demo_messages:
        print('--- NEXT TURN ---')
        print(f'Adam: {message["content"]}')
        
        try:            
            system_prompt = create_system_prompt(previous_summarization)  
            assistant_response = openai_service.completion(
                [system_prompt, message],
                "gpt-4o",
                False
            )
            
            print(f'Alice: {assistant_response.choices[0].message.content}')
            
            # Generate new summarization
            previous_summarization = await generate_summarization(message, assistant_response.choices[0].message)
            
        except Exception as e:
            print(f"Error in OpenAI completion: {e}")
            return JSONResponse(status_code=500, content={"error": "An error occurred while processing your request"})
    
    return JSONResponse(content=assistant_response)

# Run the server when the script is executed directly
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=3000, reload=True)

    response = openai_service.completion(
        [summarization_prompt, {"role": "user", "content": "Please create/update our conversation summary."}],
        "gpt-4o-mini",
        False
    )
    
    #return response.choices[0].message.content or "No conversation history"

# Function to create system prompt
def create_system_prompt(summarization: str) -> Dict[str, str]:
    content = "You are Alice, a helpful assistant who speaks using as few words as possible."
    
    if summarization:
        content += f"""

Here is a summary of the conversation so far: 
<conversation_summary>
  {summarization}
</conversation_summary>"""
    
    content += "\n\nLet's chat!"
    
    return {
        "role": "system",
        "content": content
    }

# Chat endpoint POST /api/chat
@app.post("/api/chat")
async def chat(request: Request):
    global previous_summarization
    
    try:
        data = await request.json()
        message = data.get("message")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        system_prompt = create_system_prompt(previous_summarization)
        
        assistant_response = openai_service.completion(
            [system_prompt, message],
            "gpt-4o",
            False
        )
        
        # Generate new summarization
        previous_summarization = await generate_summarization(message, assistant_response.choices[0].message)
        
        return JSONResponse(content=assistant_response)
    
    except Exception as e:
        print(f"Error in OpenAI completion: {e}")
        return JSONResponse(status_code=500, content={"error": "An error occurred while processing your request"})

# Demo endpoint POST /api/demo
@app.post("/api/demo")
async def demo():
    global previous_summarization
    
    demo_messages = [
        {"content": "Hi! I'm Adam", "role": "user"},
        {"content": "How are you?", "role": "user"},
        {"content": "Do you know my name?", "role": "user"}
    ]
    
    assistant_response = None
    
    for message in demo_messages:
        print('--- NEXT TURN ---')
        print(f'Adam: {message["content"]}')
        
        try:
            system_prompt = create_system_prompt(previous_summarization)
            
            assistant_response = openai_service.completion(
                [system_prompt, message],
                "gpt-4o",
                False
            )
            
            print(f'Alice: {assistant_response.choices[0].message.content}')
            
            # Generate new summarization
            previous_summarization = await generate_summarization(message, assistant_response.choices[0].message)
            
        except Exception as e:
            print(f"Error in OpenAI completion: {e}")
            return JSONResponse(status_code=500, content={"error": "An error occurred while processing your request"})
    
    return JSONResponse(content=assistant_response)

# Run the server when the script is executed directly
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=3000, reload=True)

# Function to create system prompt
def create_system_prompt(summarization: str) -> Dict[str, str]:
    content = "You are Alice, a helpful assistant who speaks using as few words as possible."
    
    if summarization:
        content += f"""

Here is a summary of the conversation so far: 
<conversation_summary>
  {summarization}
</conversation_summary>"""
    
    content += "\n\nLet's chat!"
    
    return {
        "role": "system",
        "content": content
    }

# Chat endpoint POST /api/chat
@app.post("/api/chat")
async def chat(request: Request):
    global previous_summarization
    
    try:
        data = await request.json()
        message = data.get("message")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        system_prompt = create_system_prompt(previous_summarization)
        
        assistant_response = openai_service.completion(
            [system_prompt, message],
            "gpt-4o",
            False
        )
        
        # Generate new summarization
        previous_summarization = await generate_summarization(message, assistant_response.choices[0].message)
        
        return JSONResponse(content=assistant_response)
    
    except Exception as e:
        print(f"Error in OpenAI completion: {e}")
        return JSONResponse(status_code=500, content={"error": "An error occurred while processing your request"})

# Demo endpoint POST /api/demo
@app.post("/api/demo")
async def demo():
    global previous_summarization
    
    demo_messages = [
        {"content": "Hi! I'm Adam", "role": "user"},
        {"content": "How are you?", "role": "user"},
        {"content": "Do you know my name?", "role": "user"}
    ]
    
    assistant_response = None
    
    for message in demo_messages:
        print('--- NEXT TURN ---')
        print(f'Adam: {message["content"]}')
        
        try:            
            system_prompt = create_system_prompt(previous_summarization)  
            assistant_response = openai_service.completion(
                [system_prompt, message],
                "gpt-4o",
                False
            )
            
            print(f'Alice: {assistant_response.choices[0].message.content}')
            
            # Generate new summarization
            previous_summarization = await generate_summarization(message, assistant_response.choices[0].message)
            
        except Exception as e:
            print(f"Error in OpenAI completion: {e}")
            return JSONResponse(status_code=500, content={"error": "An error occurred while processing your request"})
    
    return JSONResponse(content=assistant_response)

# Run the server when the script is executed directly
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=3000, reload=True)
