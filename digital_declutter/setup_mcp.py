import json
import os
from dotenv import load_dotenv

def setup_mcp():
    print("Setting up MCP configuration...")
    
    # Load .env
    load_dotenv()
    notion_token = os.getenv("NOTION_TOKEN")
    
    if not notion_token:
        print("Warning: NOTION_TOKEN not found in .env")

    # Create config with only Notion (Gmail uses custom tools)
    config = {
      "mcpServers": {
        "notion": {
          "command": "npx",
          "args": ["-y", "@notionhq/notion-mcp-server"],
          "env": {
            "NOTION_API_KEY": notion_token or ""
          }
        }
      }
    }

    with open("mcp_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("mcp_config.json created successfully!")
    print(f"Notion API Key configured: {'Yes' if notion_token else 'No'}")

if __name__ == "__main__":
    setup_mcp()
