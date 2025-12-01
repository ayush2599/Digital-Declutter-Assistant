import os
import json
import sys
from mcp_server_notion import create_notion_task

def load_config():
    try:
        with open('mcp_config.json', 'r') as f:
            config = json.load(f)
            env_vars = config['mcpServers']['notion']['env']
            os.environ['NOTION_API_KEY'] = env_vars['NOTION_API_KEY']
            os.environ['NOTION_DATABASE_ID'] = env_vars['NOTION_DATABASE_ID']
            print("Loaded credentials from mcp_config.json")
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def test_rich_task_creation():
    print("Testing creation of Notion task with all properties...")
    
    result = create_notion_task(
        title="Test Task with Metadata",
        description="This task verifies that Sender, Action Item, and Dates are populated correctly.",
        sender="Test Sender <test@example.com>",
        action_item="Verify database columns",
        due_date="2025-12-31",
        received_on="2025-11-30"
    )
    
    print("\nResult:")
    print(result)

if __name__ == "__main__":
    load_config()
    test_rich_task_creation()
