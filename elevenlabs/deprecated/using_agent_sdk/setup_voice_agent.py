#!/usr/bin/env python3
"""
Setup script for the ElevenLabs Voice Agent
This script helps users configure the voice agent environment and dependencies.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_voice_agent.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        create_env_file()
        return False
    
    print("✅ .env file exists")
    
    # Check for required variables
    required_vars = ["ELEVENLABS_API_KEY", "ELEVENLABS_AGENT_ID"]
    missing_vars = []
    
    with open(env_file, "r") as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=" in content and f"{var}=your_" in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with the correct values")
        return False
    
    print("✅ Environment variables configured")
    return True

def create_env_file():
    """Create a template .env file"""
    env_content = """# ElevenLabs Voice Agent Configuration
# Required: Get your API key from https://elevenlabs.io
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Required: Create an agent in ElevenLabs dashboard and get its ID
ELEVENLABS_AGENT_ID=your_agent_id_here

# Optional: For enhanced file editing features
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Enable debug mode
DEBUG=false
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("📝 Created .env file template")
    print("Please edit .env file and add your actual API keys and agent ID")

def check_backend_connection():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI backend is running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("⚠️  FastAPI backend is not running")
    print("Please start the backend server first:")
    print("  python main.py")
    return False

def test_elevenlabs_connection():
    """Test connection to ElevenLabs API"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key or api_key == "your_elevenlabs_api_key_here":
            print("⚠️  ElevenLabs API key not configured")
            return False
        
        # Test API connection
        headers = {"xi-api-key": api_key}
        response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ ElevenLabs API connection successful")
            return True
        else:
            print(f"❌ ElevenLabs API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test ElevenLabs connection: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 ElevenLabs Voice Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check environment configuration
    env_configured = check_env_file()
    
    # Test connections
    backend_running = check_backend_connection()
    
    if env_configured:
        elevenlabs_connected = test_elevenlabs_connection()
    else:
        elevenlabs_connected = False
    
    print("\n" + "=" * 40)
    print("📋 Setup Summary:")
    print(f"  Python Version: ✅")
    print(f"  Dependencies: ✅")
    print(f"  Environment: {'✅' if env_configured else '⚠️'}")
    print(f"  Backend: {'✅' if backend_running else '⚠️'}")
    print(f"  ElevenLabs API: {'✅' if elevenlabs_connected else '⚠️'}")
    
    if env_configured and backend_running and elevenlabs_connected:
        print("\n🎉 Setup complete! You can now run the voice agent:")
        print("  python voice_agent.py")
    else:
        print("\n⚠️  Setup incomplete. Please address the issues above.")
        if not env_configured:
            print("\n📝 Next steps:")
            print("1. Edit .env file with your actual API keys")
            print("2. Create an ElevenLabs agent and get its ID")
            print("3. Run this setup script again")
        
        if not backend_running:
            print("\n🔧 Backend setup:")
            print("1. Start the FastAPI backend: python main.py")
            print("2. Ensure it's running on http://localhost:8001")
    
    return env_configured and backend_running and elevenlabs_connected

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
