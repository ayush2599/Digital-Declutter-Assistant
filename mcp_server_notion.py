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
def create_notion_task(title: str, description: str = "") -> str:
    """
    Create a new task in the Notion database.
    
    Args:
        title: The title of the task
        description: A description or details for the task
        
    Returns:
        A success message with the URL of the created task, or an error message.
    """
    try:
        client = get_notion_client()
        database_id = os.environ.get("NOTION_DATABASE_ID")
        
        if not database_id:
            return "Error: NOTION_DATABASE_ID environment variable is not set"

        # Create the page in the database
        new_page = client.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {  # Assuming the title property is named "Name" or "Title"
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
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
