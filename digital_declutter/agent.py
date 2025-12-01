import os
import json
from typing import List
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv
from .preferences import PreferenceStore
from .tools.gmail_tool import GmailService

# Load environment variables
load_dotenv()

# Global services
_preference_store = None
_gmail_service = None

def get_prefs():
    global _preference_store
    if not _preference_store:
        _preference_store = PreferenceStore()
    return _preference_store

def get_gmail():
    global _gmail_service
    if not _gmail_service:
        _gmail_service = GmailService()
    return _gmail_service

# --- Preference Tools ---

def get_user_rules(sender: str) -> str:
    """
    Checks if there is a saved rule for a specific sender.
    Returns the rule (e.g., 'always_delete', 'always_important') or 'no_rule'.
    """
    prefs = get_prefs()
    rule = prefs.get_rule(sender)
    return rule if rule else "no_rule"

def save_user_rule(sender: str, rule: str) -> str:
    """
    Saves a rule for a specific sender.
    Args:
        sender: The email address or name of the sender.
        rule: The rule to save (e.g., 'always_delete', 'always_important').
    """
    prefs = get_prefs()
    prefs.set_rule(sender, rule)
    return f"Rule saved: Emails from '{sender}' will be treated as '{rule}'."

def get_all_rules() -> str:
    """
    Returns all saved user rules.
    """
    prefs = get_prefs()
    rules = prefs.get_all_rules()
    if not rules:
        return "No rules saved yet."
    return f"Current Rules:\n{rules}"

# --- Gmail Tools (Custom) ---

def fetch_inbox_emails(days: int = 3, max_results: int = 20) -> str:
    """
    Fetches recent emails from the inbox.
    Args:
        days: Number of days to look back (default: 3)
        max_results: Maximum number of emails to fetch (default: 20)
    Returns:
        A formatted string with email details
    """
    gmail = get_gmail()
    emails = gmail.fetch_recent_emails(days=days, max_results=max_results)
    
    if not emails:
        return "No emails found."
    
    result = f"Found {len(emails)} emails:\n\n"
    for i, email in enumerate(emails, 1):
        result += f"{i}. ID: {email['id']}\n"
        result += f"   From: {email['sender']}\n"
        result += f"   Subject: {email['subject']}\n"
        result += f"   Date: {email['date']}\n"
        result += f"   Snippet: {email['snippet'][:100]}...\n\n"
    
    return result

def trash_email(email_id: str) -> str:
    """
    Moves an email to trash.
    Args:
        email_id: The Gmail message ID
    """
    gmail = get_gmail()
    success = gmail.trash_email(email_id)
    return f"Email {email_id} moved to trash." if success else f"Failed to trash email {email_id}."

def archive_email(email_id: str) -> str:
    """
    Archives an email (removes from inbox).
    Args:
        email_id: The Gmail message ID
    """
    gmail = get_gmail()
    success = gmail.archive_email(email_id)
    return f"Email {email_id} archived." if success else f"Failed to archive email {email_id}."

# --- Agent Definition ---

async def create_agent(model_name="gemini-2.5-flash-lite", mcp_config_path="mcp_config.json"):
    """Creates and returns the Digital Declutter Agent with hybrid tools (custom Gmail + MCP Notion)."""
    
    print("Initializing Digital Declutter Agent...")
    
    # Load Notion MCP Tools
    mcp_tools = []
    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
                
            servers = config.get("mcpServers", {})
            for server_name, server_config in servers.items():
                print(f"Initializing MCP server: {server_name}")
                try:
                    # Create connection params with increased timeout
                    conn_params = StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command=server_config["command"],
                            args=server_config["args"],
                            env=server_config.get("env")
                        ),
                        timeout=60  # Increase timeout to 60 seconds
                    )
                    
                    # Create toolset
                    toolset = McpToolset(connection_params=conn_params)
                    tools = await toolset.get_tools()
                    mcp_tools.extend(tools)
                    print(f"✅ Successfully loaded {len(tools)} tools from {server_name}")
                    for tool in tools:
                        print(f"   - {tool.name}")
                except Exception as e:
                    print(f"❌ Failed to load MCP server {server_name}: {e}")
                    print(f"   Error type: {type(e).__name__}")
        except Exception as e:
            print(f"Error reading MCP config: {e}")
    else:
        print(f"Warning: MCP config not found at {mcp_config_path}")

    # Load Notion database ID from environment
    notion_db_id = os.getenv("NOTION_DATABASE_ID", "2b8c3719a408805a9871ce867656d1e7")
    
    instruction = f"""
    You are the Digital Declutter Assistant. Your goal is to help the user triage their inbox intelligently.
    
    **Tools Available:**
    *   Gmail tools: `fetch_inbox_emails`, `trash_email`, `archive_email`
    *   Notion tools: via MCP (for creating tasks)
    *   User Preference tools: `get_user_rules`, `save_user_rule`, `get_all_rules`
    
    **Notion Configuration:**
    *   Database ID: {notion_db_id} (already configured, never ask for it)
    
    **Email Summary Format:**
    When listing emails, ALWAYS include:
    - Sender
    - Subject
    - **Received Date** (from the email's Date field)
    - Brief summary
    
    **Task Creation Intelligence:**
    When user says "create a task" or "this is important":
    1. **Automatically** create the task without asking for title
    2. Generate a smart title from: Subject + key action items
    3. Include in task body: Email summary, sender, date, and any deadlines mentioned
    4. Extract due dates from email content if mentioned
    5. **Never ask** the user for task details - be intelligent and autonomous
    
    **Sender Rules & Memory:**
    - When user says "this sender is always important/promotional/spam", use `save_user_rule(sender, rule)`
    - **Always** check `get_all_rules()` at the start to apply saved preferences
    - Rules: 'always_important', 'always_archive', 'always_trash', 'promotional'
    
    **Workflow & Proactivity:**
    1. **Start**: Check `get_all_rules()` to load user preferences.
    2. **Fetch**: Get emails using `fetch_inbox_emails`.
    3. **Analyze & Categorize (IMMEDIATELY)**:
       - Group emails into: **Important**, **Promotional**, **Spam**, **FYI/Neutral**.
       - Apply saved rules (e.g., if 'always_important', put in Important).
       - Use your judgment for others based on sender/subject.
    4. **Present & Recommend**:
       - Show the categorized list.
       - **Propose an Action Plan**: "I recommend creating tasks for the Important ones and archiving the Promotional ones. Shall I proceed?"
       - **DO NOT** just list emails and ask "What next?". **Always suggest the next step.**
    5. **Execute**: Wait for user confirmation, then run the tools (create tasks, archive, etc.).

    **Categorization Logic:**
    - **Important**: Personal emails, work updates, security alerts, bills, or senders marked 'always_important'.
    - **Promotional**: Newsletters, marketing, sales, job alerts (unless user is job hunting).
    - **Spam**: Obvious junk.
    - **FYI**: Notifications, social updates, receipts.

    **Presentation & Formatting:**
    - Use **Markdown** to make the output beautiful and readable.
    - Use `###` headers for categories (e.g., `### 🚨 Important`, `### 📢 Promotional`).
    - Use bullet points for emails.
    - **Bold** the sender and subject for clarity.
    - Use `> ` blockquotes for the action plan/recommendation at the end to make it stand out.
    - Example format:
      ### 🚨 Important
      *   **Sender**: Subject (Date) - _Summary_
      
      ### 📢 Promotional
      *   **Sender**: Subject (Date) - _Summary_
      
      > **Recommendation**: I suggest creating tasks for the Important emails...
    """
    
    # Combine custom Gmail tools, preference tools, and MCP Notion tools
    gmail_tools = [fetch_inbox_emails, trash_email, archive_email]
    preference_tools = [get_user_rules, save_user_rule, get_all_rules]
    all_tools = preference_tools + gmail_tools + mcp_tools
    
    print(f"\nAgent configured with {len(all_tools)} tools total:")
    print(f"  - {len(preference_tools)} preference tools")
    print(f"  - {len(gmail_tools)} Gmail tools")
    print(f"  - {len(mcp_tools)} Notion MCP tools")
    
    return LlmAgent(
        name="DigitalDeclutter",
        model=Gemini(model=model_name),
        instruction=instruction,
        tools=all_tools
    )
