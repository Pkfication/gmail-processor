from src.gmail.auth import authenticate

def main():
    print("Starting Gmail authentication...")
    service = authenticate()
    print("Authentication successful!")
    print("You can now use the Gmail API.")

if __name__ == "__main__":
    main() 