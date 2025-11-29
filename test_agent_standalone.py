import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'digital_declutter')))

from digital_declutter.agent import create_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

async def main():
    print("Initializing Agent...")
    try:
        agent = await create_agent(model_name="gemini-2.5-flash-lite", mcp_config_path="mcp_config.json")
        print("Agent initialized.")
        
        session_service = InMemorySessionService()
        runner = Runner(agent=agent, app_name="test_app", session_service=session_service)
        
        session_id = "test_session"
        await session_service.create_session(app_name="test_app", user_id="user", session_id=session_id)
        
        print("Sending message: Clean my inbox")
        message = types.Content(parts=[types.Part(text="Clean my inbox")])
        
        async for event in runner.run_async(user_id="user", session_id=session_id, new_message=message):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        print(f"Agent: {part.text}")
                        
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    with open("standalone_log.txt", "w") as f:
        sys.stdout = f
        sys.stderr = f
        asyncio.run(main())
