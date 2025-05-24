# Gmail Rule-Based Email Processor

This project implements a rule-based email processing system that integrates with Gmail API to automate email management tasks.

## Features

- Gmail API integration using OAuth2 authentication
- Email storage in SQLite database (stored locally in `gmail_processor.db`)
- Rule-based email processing with configurable conditions and actions
- Support for various email fields (From, Subject, Message, Received Date)
- Multiple predicate types for different field types
- Actions: Mark as read/unread, Move message

## Prerequisites

- Python 3.8+
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials

## Setup

1. Clone the repository:

```bash
git clone git@github.com:Pkfication/gmail-processor.git
cd gmail-rule-processor
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies and the package in development mode:

```bash
pip install -r requirements.txt
```

4. Set up Google Cloud Project:

   - Go to Google Cloud Console
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download credentials and save as `credentials.json` in the project root directory

5. Set up environment variables:
   Create a `.env` file in the project root with the following variables:

```
GOOGLE_CREDENTIALS_FILE=credentials.json
```

6. Initialize the database:

```bash
python -m scripts.init_db
```

## Usage

1. First-time authentication:

```bash
python -m scripts.auth
```

2. Fetch emails:

```bash
python -m scripts.fetch_emails
```

3. Process emails with rules:

```bash
python -m scripts.process_emails
```

## Rule Configuration

Rules are defined in `config/rules.json`. Example:

```json
{
  "rules": [
    {
      "name": "Newsletter Processing",
      "predicate": "all",
      "conditions": [
        {
          "field": "subject",
          "predicate": "contains",
          "value": "newsletter"
        },
        {
          "field": "from",
          "predicate": "contains",
          "value": "example.com"
        }
      ],
      "actions": [
        {
          "type": "mark_as_read"
        },
        {
          "type": "move_to",
          "value": "Newsletters"
        }
      ]
    }
  ]
}
```

## Testing

Run tests using pytest:

```bash
python -m pytest tests/ -v
```

## Project Structure

```
gmail-rule-processor/
├── config/
│   └── rules.json
├── scripts/
│   ├── auth.py
│   ├── fetch_emails.py
│   ├── init_db.py
│   └── process_emails.py
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── session.py
│   ├── gmail/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── client.py
│   └── rules/
│       ├── __init__.py
│       ├── engine.py
│       └── parser.py
├── tests/
│   ├── test_database.py
│   ├── test_gmail.py
│   └── test_rules.py
├── credentials.json    # Place your Google OAuth credentials here
├── gmail_processor.db
├── .env
├── requirements.txt
└── README.md
```
