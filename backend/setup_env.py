"""
Setup script for environment variables.
"""

import os

def create_env_file():
    """Create a .env file with template values."""
    
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=150
OPENAI_RETRY_ATTEMPTS=3

# Session Configuration
SESSION_TIMEOUT_MINUTES=30

# Serper API (for future use)
SERPER_API_KEY=your_serper_api_key_here
"""
    
    env_file_path = ".env"
    
    if os.path.exists(env_file_path):
        print(f"⚠️  .env file already exists at {env_file_path}")
        print("Please edit it manually to add your API keys.")
    else:
        with open(env_file_path, "w") as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file_path}")
        print("Please edit it to add your actual API keys:")
        print("1. Replace 'your_openai_api_key_here' with your OpenAI API key")
        print("2. Replace 'your_serper_api_key_here' with your Serper API key (optional)")
    
    print("\nTo get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print("3. Copy the key and paste it in the .env file")

def check_env_setup():
    """Check if environment variables are properly set."""
    
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🔍 Checking environment setup...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set or using placeholder value")
        print("Please add your OpenAI API key to the .env file")
        return False
    else:
        print("✅ OPENAI_API_KEY is set")
    
    if serper_key and serper_key != "your_serper_api_key_here":
        print("✅ SERPER_API_KEY is set")
    else:
        print("ℹ️  SERPER_API_KEY not set (optional)")
    
    return True

if __name__ == "__main__":
    print("🚀 Environment Setup for AI Chat")
    print("=" * 40)
    
    create_env_file()
    print()
    check_env_setup()
    
    print("\n📝 Next steps:")
    print("1. Edit the .env file with your actual API keys")
    print("2. Run: python test_chat.py")
    print("3. Start the server: python main.py") 