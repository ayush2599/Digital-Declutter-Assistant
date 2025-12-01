import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import nest_asyncio
import asyncio

# Add parent directory to path to import digital_declutter
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from digital_declutter.agent import create_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Apply nest_asyncio to allow nested event loops if needed
nest_asyncio.apply()

app = FastAPI(title="Digital Declutter Assistant API")

# Global variables to hold agent and runner
agent = None
runner = None
session_service = None
agent_init_lock = asyncio.Lock()
APP_NAME = "declutter_app"
SESSION_ID = "session_1"
USER_ID = "user"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

async def ensure_agent_initialized():
    """Initialize agent lazily on first request to avoid MCP startup issues"""
    global agent, runner, session_service
    
    async with agent_init_lock:
        if agent is not None:
            return  # Already initialized
        
        print("Initializing Agent (lazy)...")
        mcp_config_path = os.path.join(os.path.dirname(__file__), '..', 'mcp_config.json')
        
        try:
            agent = await create_agent(model_name="gemini-2.5-flash-lite", mcp_config_path=mcp_config_path)
            session_service = InMemorySessionService()
            runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
            
            # Create session
            await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
            print("Agent initialized successfully!")
        except Exception as e:
            print(f"Error initializing agent: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=503, detail=f"Failed to initialize agent: {str(e)}")

def debug_log(message: str):
    """Log message to debug.log with timestamp"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(log_entry)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    debug_log(f"Received chat request: {request.message}")
    
    # Initialize agent on first request
    try:
        await ensure_agent_initialized()
    except Exception as e:
        debug_log(f"Agent initialization failed: {e}")
        raise HTTPException(status_code=503, detail=f"Agent initialization failed: {e}")
    
    global runner
    if not runner:
        debug_log("Error: Agent not initialized after ensure_agent_initialized")
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        message = types.Content(parts=[types.Part(text=request.message)])
        full_response = ""
        
        debug_log("Starting agent run loop...")
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
            # Log event type
            event_type = type(event).__name__
            debug_log(f"Event received: {event_type}")
            
            if hasattr(event, 'content') and event.content:
                debug_log(f"Event content: {event.content}")
            
            # Capture text from any event that has it
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        debug_log(f"Text part received: {part.text[:50]}...")
                        full_response += part.text
            
            # Check for tool calls
            if hasattr(event, 'tool_call') and event.tool_call:
                debug_log(f"Tool Call: {event.tool_call}")
            if hasattr(event, 'tool_response') and event.tool_response:
                debug_log(f"Tool Response: {event.tool_response}")

        debug_log(f"Agent run completed. Final response length: {len(full_response)}")
        return ChatResponse(response=full_response)
        
    except Exception as e:
        import traceback
        error_msg = f"Error during chat: {e}\n{traceback.format_exc()}"
        debug_log(f"EXCEPTION: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "agent_initialized": agent is not None}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
