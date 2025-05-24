import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
from .auth import get_gmail_service

class GmailClient:
    def __init__(self):
        self.service = get_gmail_service()

    def list_messages(self, max_results=100):
        """List messages in the user's mailbox."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            return results.get('messages', [])
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_message(self, msg_id):
        """Get a specific message by ID."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def parse_message(self, message):
        """Parse a Gmail message into a dictionary."""
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        from_address = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        to_address = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        
        # Parse the message body
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode()

        return {
            'gmail_id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'from_address': from_address,
            'to_address': to_address,
            'message': body,
            'received_date': datetime.fromtimestamp(int(message['internalDate'])/1000),
            'is_read': 'UNREAD' not in message['labelIds'] if 'labelIds' in message else False
        }

    def mark_as_read(self, msg_id):
        """Mark a message as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def mark_as_unread(self, msg_id):
        """Mark a message as unread."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def move_message(self, msg_id, label_name):
        """Move a message to a specific label."""
        try:
            # First, get or create the label
            labels = self.service.users().labels().list(userId='me').execute()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'].lower() == label_name.lower():
                    label_id = label['id']
                    break
            
            if not label_id:
                # Create new label
                label = self.service.users().labels().create(
                    userId='me',
                    body={'name': label_name}
                ).execute()
                label_id = label['id']
            
            # Apply the label
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False 