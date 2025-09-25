#!/usr/bin/env python3
"""
Simple launcher for AI Assistant with audio
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from audio_client import AudioAssistant

def print_welcome():
    """Print welcome message"""
    print("🎤" + "=" * 60 + "🎤")
    print("           AI ASSISTANT - VOICE INTERFACE")
    print("🎤" + "=" * 60 + "🎤")
    print()
    print("🎯 This AI assistant can help you with:")
    print("   • Blog writing sessions")
    print("   • Creative storytelling (improv games)")
    print("   • Email writing workshops")
    print("   • Brainstorming sessions")
    print("   • Interview preparation")
    print()
    print("💬 Just speak naturally! Try saying:")
    print("   'Start a blog writing session'")
    print("   'Let's play an improv game'")
    print("   'Help me brainstorm ideas'")
    print()
    print("📁 Generated content will be saved in the 'workspace' folder")
    print("🛑 Press Ctrl+C anytime to stop")
    print()

def check_requirements():
    """Check if required packages are installed"""
    try:
        import pyaudio
        import openai
        import numpy
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n📦 Please install requirements:")
        print("pip install -r requirements.txt")
        return False

def check_env():
    """Check if OpenAI API key is set"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not found!")
        print("\n🔑 Please set your API key:")
        print("export OPENAI_API_KEY=your_api_key_here")
        print("Or add it to your .env file")
        return False
    return True

async def main():
    """Main function"""
    print_welcome()
    
    # Check requirements
    if not check_requirements():
        return
    
    if not check_env():
        return
    
    # Create and start assistant
    assistant = AudioAssistant()
    
    print("🔍 Checking audio devices...\n")
    assistant.list_audio_devices()
    
    # Simple device selection
    print("🎛️  Audio Device Selection:")
    print("   • Press Enter to use default devices (recommended)")
    print("   • Or enter device numbers from the list above")
    print()
    
    try:
        input_choice = input("Input device (microphone) [default]: ").strip()
        input_device = int(input_choice) if input_choice else None
        
        output_choice = input("Output device (speakers) [default]: ").strip()
        output_device = int(output_choice) if output_choice else None
        
    except (ValueError, KeyboardInterrupt):
        print("\n🎧 Using default audio devices...")
        input_device = None
        output_device = None
    
    print("\n🚀 Starting AI Assistant...")
    print("━" * 60)
    
    try:
        await assistant.start(input_device, output_device)
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using AI Assistant!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   • Check your internet connection")
        print("   • Verify your OpenAI API key")
        print("   • Make sure your microphone is working")
        print("   • Try running: python test_system.py")
    finally:
        assistant.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Startup error: {e}")
        sys.exit(1)