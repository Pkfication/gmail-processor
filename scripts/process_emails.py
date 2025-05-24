from src.gmail.client import GmailClient
from src.database.session import SessionLocal
from src.database.models import Email
from src.rules.engine import RuleEngine
from src.rules.parser import RuleParser
import os
import sys

def process_emails():
    """Process emails based on rules."""
    gmail_client = GmailClient()
    db = SessionLocal()
    rules_file = os.path.join('config', 'rules.json')
    
    try:
        # Load rules
        rule_parser = RuleParser(rules_file)
        rules = rule_parser.get_rules_from_db(db)
        
        if not rules:
            print("No rules found in database. Loading from JSON file...")
            rules = rule_parser.save_rules_to_db(db)
        
        if not rules:
            print("No rules found. Please create rules in config/rules.json")
            return
        
        print(f"Loaded {len(rules)} rules")
        
        # Initialize rule engine
        rule_engine = RuleEngine(gmail_client)
        
        # Get unprocessed emails
        emails = db.query(Email).all()
        print(f"Processing {len(emails)} emails")
        
        # Process each email
        for email in emails:
            # Refresh the email object to ensure it's bound to the current session
            db.refresh(email)
            results = rule_engine.process_email(email, rules)
            if results:
                print(f"Email {email.gmail_id} matched rules:")
                for result in results:
                    print(f"  Rule: {result['rule_name']}")
                    for action in result['actions']:
                        status = "successful" if action['success'] else "failed"
                        print(f"    Action: {action['action_type']} - {status}")
            
    except Exception as e:
        print(f"Error processing emails: {e}")
        sys.exit(1)
    finally:
        db.close()

def main():
    print("Starting email processing...")
    process_emails()
    print("Email processing completed!")

if __name__ == "__main__":
    main() 