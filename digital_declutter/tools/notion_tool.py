import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

class NotionService:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.token or not self.database_id:
            print("Warning: NOTION_TOKEN or NOTION_DATABASE_ID not set in .env")
            self.client = None
        else:
            self.client = Client(auth=self.token)

    def create_task(self, title, summary, due_date=None, link=None):
        """Creates a task in the Notion database."""
        if not self.client:
            return False

        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
        }
        
        # Add date if provided (assuming standard Notion date property 'Date')
        if due_date:
             properties["Date"] = {"date": {"start": due_date}}

        # Add link if provided (assuming URL property 'Link' or just append to body)
        # For simplicity, we'll put the link and summary in the page content (children)
        
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": summary}}]
                }
            }
        ]
        
        if link:
             children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "Source Email: "}},
                        {"type": "text", "text": {"content": "Open in Gmail", "link": {"url": link}}}
                    ]
                }
            })

        try:
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            print(f"Task '{title}' created in Notion.")
            return True
        except Exception as e:
            print(f"Error creating Notion task: {e}")
            return False

if __name__ == '__main__':
    # Test the service
    notion = NotionService()
    if notion.client:
        notion.create_task("Test Task from Agent", "This is a test summary.", link="https://mail.google.com")
