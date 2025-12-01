import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from notion_client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("notion-server")

def get_notion_client():
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        raise ValueError("NOTION_API_KEY environment variable is not set")
    return Client(auth=api_key)

@mcp.tool()
def create_notion_task(
    title: str, 
    description: str = "", 
    sender: str = "", 
    action_item: str = "", 
    due_date: str = "", 
    received_on: str = ""
) -> str:
    """
    Create a new task in the Notion database with detailed metadata.
    
    Args:
        title: The title of the task (maps to 'Task' property)
        description: A description or details for the task (added as page content)
        sender: The sender of the email (maps to 'Sender' property)
        action_item: The specific action required (maps to 'Action Item' property)
        due_date: Due date in ISO 8601 format (YYYY-MM-DD) (maps to 'Due Date' property)
        received_on: Date received in ISO 8601 format (YYYY-MM-DD) (maps to 'Received On' property)
        
    Returns:
        A success message with the URL of the created task, or an error message.
    """
    try:
        client = get_notion_client()
        database_id = os.environ.get("NOTION_DATABASE_ID")
        
        if not database_id:
            return "Error: NOTION_DATABASE_ID environment variable is not set"

        # Construct properties
        properties = {
            "Task": {  # Title property renamed to "Task" by user
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        # Add optional properties if provided
        if sender:
            # Try to extract email if it's in "Name <email>" format
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', sender)
            email_val = email_match.group(0) if email_match else sender
            
            # Assuming 'Sender' is an Email property based on error "Expected to be email"
            # If it were Text, we would use rich_text. But let's try Email first.
            properties["Sender"] = {
                "email": email_val
            }
            
        if action_item:
            properties["Action Item"] = {
                "rich_text": [{"text": {"content": action_item}}]
            }
            
        if due_date:
            properties["Due Date"] = {
                "date": {"start": due_date}
            }
            
        if received_on:
            properties["Received On"] = {
                "date": {"start": received_on}
            }

        # Create the page in the database
        new_page = client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": description
                                }
                            }
                        ]
                    }
                }
            ]
        )
        
        return f"Successfully created Notion task: {title}\nURL: {new_page.get('url')}"
        
    except Exception as e:
        logger.error(f"Failed to create Notion task: {e}")
        return f"Error creating Notion task: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
