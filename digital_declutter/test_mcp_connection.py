import asyncio
import os
import json
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

async def test_mcp():
    print("Testing MCP Connection...")
    mcp_config_path = "mcp_config.json"
    
    if not os.path.exists(mcp_config_path):
        print("Config not found")
        return

    with open(mcp_config_path, 'r') as f:
        config = json.load(f)
        
    servers = config.get("mcpServers", {})
    for server_name, server_config in servers.items():
        print(f"--- Testing {server_name} ---")
        try:
            conn_params = StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=server_config["command"],
                    args=server_config["args"],
                    env=server_config.get("env")
                )
            )
            
            toolset = McpToolset(connection_params=conn_params)
            tools = await toolset.get_tools()
            print(f"SUCCESS: Loaded {len(tools)} tools from {server_name}")
        except Exception as e:
            print(f"FAILURE: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    with open("test_mcp_log.txt", "w") as log_file:
        import sys
        sys.stdout = log_file
        sys.stderr = log_file
        asyncio.run(test_mcp())
