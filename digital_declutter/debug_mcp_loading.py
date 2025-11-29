import os
import json
import sys
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Load env
load_dotenv()

def debug_mcp_loading():
    print(f"Current Working Directory: {os.getcwd()}")
    config_path = "mcp_config.json"
    
    if not os.path.exists(config_path):
        # Try looking in digital_declutter/ if running from root
        if os.path.exists(f"digital_declutter/{config_path}"):
            config_path = f"digital_declutter/{config_path}"
        else:
            print(f"ERROR: {config_path} not found!")
            return

    print(f"Found config at: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        servers = config.get("mcpServers", {})
        print(f"Servers found in config: {list(servers.keys())}")
        
        for server_name, server_config in servers.items():
            print(f"\n--- Attempting to load {server_name} ---")
            print(f"Command: {server_config['command']}")
            print(f"Args: {server_config['args']}")
            # Mask env vars for security in logs
            env_keys = list(server_config.get("env", {}).keys())
            print(f"Env Vars: {env_keys}")
            
            try:
                conn_params = StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=server_config["command"],
                        args=server_config["args"],
                        env=server_config.get("env")
                    )
                )
                print("Connection params created.")
                
                print("Initializing McpToolset...")
                toolset = McpToolset(connection_params=conn_params)
                
                print("Fetching tools...")
                tools = toolset.get_tools()
                
                print(f"SUCCESS: Loaded {len(tools)} tools.")
                for t in tools:
                    print(f" - {t.name}")
                    
            except Exception as e:
                print(f"FAILURE loading {server_name}: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    with open("debug_log.txt", "w") as log_file:
        sys.stdout = log_file
        sys.stderr = log_file
        debug_mcp_loading()
