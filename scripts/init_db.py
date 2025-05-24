from src.database.session import init_db

def main():
    print("Initializing database...")
    init_db()
    print("Database initialization completed!")

if __name__ == "__main__":
    main() 