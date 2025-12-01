import os
import datetime
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailService:
    def __init__(self, credentials_path=None, token_path=None):
        print(f"DEBUG: Loading GmailService from {__file__}")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to digital_declutter root if needed, or assume they are in the same dir as the package
        # Actually, based on file structure: digital_declutter/credentials.json
        # and this file is digital_declutter/tools/gmail_tool.py
        # So we need to go up one level.
        project_root = os.path.dirname(base_dir) 
        
        if credentials_path is None:
            self.credentials_path = os.path.join(project_root, 'credentials.json')
        else:
            self.credentials_path = credentials_path
            
        if token_path is None:
            self.token_path = os.path.join(project_root, 'token.json')
        else:
            self.token_path = token_path
            
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        print(f"DEBUG: Checking for token at {self.token_path}")
        if os.path.exists(self.token_path):
            print("DEBUG: Token file found.")
            try:
                self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"DEBUG: Error loading token: {e}")
                self.creds = None
        else:
            print("DEBUG: Token file NOT found.")
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            print("DEBUG: Credentials invalid or missing. Starting auth flow...")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("DEBUG: Refreshing expired token...")
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"DEBUG: Refresh failed: {e}. forcing new login.")
                    self.creds = None
            
            if not self.creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}. Please download it from Google Cloud Console.")
                
                print("DEBUG: Launching local server for OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            print(f"DEBUG: Saving new token to {self.token_path}")
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
            print("DEBUG: Gmail service built successfully.")
        except HttpError as error:
            print(f'An error occurred: {error}')

    def fetch_recent_emails(self, days=3, max_results=50):
        """Fetches emails from the last N days."""
        if not self.service:
            self.authenticate()

        # Calculate date query
        date_after = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y/%m/%d')
        query = f'after:{date_after} -category:promotions -category:social' # Basic filtering to reduce noise, can be adjusted

        try:
            results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            email_data = []
            for msg in messages:
                msg_detail = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                payload = msg_detail.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                snippet = msg_detail.get('snippet', '')
                
                # Simple body extraction (prefer plain text)
                body = snippet # Default to snippet
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode()
                                break
                elif 'body' in payload:
                    data = payload['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()

                email_data.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': snippet,
                    'body': body[:2000] # Truncate body to avoid token limits
                })
                
            return email_data

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def trash_email(self, msg_id):
        """Moves an email to Trash."""
        try:
            self.service.users().messages().trash(userId='me', id=msg_id).execute()
            print(f"Message {msg_id} moved to Trash.")
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

    def archive_email(self, msg_id):
        """Archives an email by removing the INBOX label."""
        try:
            self.service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['INBOX']}).execute()
            print(f"Message {msg_id} archived.")
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

if __name__ == '__main__':
    # Test the service
    gmail = GmailService()
    emails = gmail.fetch_recent_emails(days=1, max_results=5)
    for email in emails:
        print(f"Subject: {email['subject']}")
