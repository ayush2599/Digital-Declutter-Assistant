import asyncio
import sys
import os

# Redirect output to file
output_file = open("test_notion_output.txt", "w", encoding="utf-8")
sys.stdout = output_file
sys.stderr = output_file

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from digital_declutter.agent import create_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def test_notion_integration():
    """Test creating a task in Notion via MCP"""
    print("=" * 60)
    print("Testing Notion MCP Integration")
    print("=" * 60)
    
    try:
        # Initialize agent
        print("\n1. Initializing agent with MCP...")
        agent = await create_agent(model_name="gemini-2.5-flash-lite", mcp_config_path="mcp_config.json")
        print("✅ Agent initialized successfully")
        
        # Create runner
        session_service = InMemorySessionService()
        runner = Runner(agent=agent, app_name="test_app", session_service=session_service)
        await session_service.create_session(app_name="test_app", user_id="test_user", session_id="test_session")
        print("✅ Runner created")
        
        # Test message
        print("\n2. Sending test message to create a Notion task...")
        test_message = "Create a test task in Notion with title 'Test Task from Agent' and description 'This is a test to verify Notion MCP integration works correctly.'"
        
        message = types.Content(parts=[types.Part(text=test_message)])
        full_response = ""
        
        async for event in runner.run_async(user_id="test_user", session_id="test_session", new_message=message):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text"):
                        full_response += part.text
            else:
                # Just print the event type or content for debugging
                pass
        
        print("\n3. Agent Response:")
        print("-" * 60)
        print(full_response)
        print("-" * 60)
        
        # Check if successful
        if "error" in full_response.lower() or "failed" in full_response.lower():
            print("\n❌ FAILED: Notion task creation encountered an error")
            return False
        else:
            print("\n✅ SUCCESS: Notion task appears to have been created")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Notion MCP Integration Test...")
    print("This will test if the agent can create tasks in Notion via MCP\n")
    
    success = asyncio.run(test_notion_integration())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Notion MCP integration is working!")
        print("You can safely restart the backend server.")
    else:
        print("❌ TEST FAILED: Notion MCP integration has issues")
        print("Recommendation: Use custom Notion tools instead of MCP")
    print("=" * 60)
    
    output_file.close()
    
    # Print to console
    with open("test_notion_output.txt", "r", encoding="utf-8") as f:
        print(f.read(), file=sys.__stdout__)
