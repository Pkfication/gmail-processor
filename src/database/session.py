from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite database file in the project directory
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///gmail_processor.db')

# Create engine with SQLite-specific configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}  # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .models import Base
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize with empty tables using SQLite-compatible commands
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM rule_actions"))
        conn.execute(text("DELETE FROM rule_conditions"))
        conn.execute(text("DELETE FROM rules"))
        conn.execute(text("DELETE FROM emails"))
        conn.commit() 