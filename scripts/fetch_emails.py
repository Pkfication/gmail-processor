from src.gmail.client import GmailClient
from src.database.session import SessionLocal
from src.database.models import Email
import sys

def fetch_emails(max_results=100):
    """Fetch emails from Gmail and store them in the database."""
    gmail_client = GmailClient()
    db = SessionLocal()
    
    try:
        # Get messages from Gmail
        messages = gmail_client.list_messages(max_results=max_results)
        print(f"Found {len(messages)} messages in Gmail")
        
        # Process each message
        for message in messages:
            # Check if email already exists in database
            existing_email = db.query(Email).filter_by(gmail_id=message['id']).first()
            if existing_email:
                continue
            
            # Get full message details
            full_message = gmail_client.get_message(message['id'])
            if not full_message:
                continue
            
            # Parse message
            email_data = gmail_client.parse_message(full_message)
            
            # Create email record
            email = Email(**email_data)
            db.add(email)
        
        db.commit()
        print("Successfully fetched and stored emails")
    
    except Exception as e:
        db.rollback()
        print(f"Error fetching emails: {e}")
        sys.exit(1)
    finally:
        db.close()

def main():
    print("Starting email fetch process...")
    fetch_emails()
    print("Email fetch process completed!")

if __name__ == "__main__":
    main() 