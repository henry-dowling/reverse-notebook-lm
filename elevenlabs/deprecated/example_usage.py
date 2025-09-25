#!/usr/bin/env python3
"""
Example usage of the ElevenLabs Voice Agent
This script demonstrates how to use the voice agent programmatically.
"""

import asyncio
import os
from dotenv import load_dotenv
from voice_agent import VoiceAgent

async def example_file_operations():
    """Example of file operations through the voice agent"""
    print("📁 Example: File Operations")
    print("-" * 30)
    
    # Initialize agent
    load_dotenv()
    agent = VoiceAgent(
        agent_id=os.getenv("ELEVENLABS_AGENT_ID"),
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )
    
    # Setup tools
    agent.setup_tools()
    
    # Example 1: List files
    print("1. Listing markdown files...")
    result = await agent.client_tools.tools["list_markdown_files"]({})
    print(f"   Result: {result}")
    
    # Example 2: Create a file
    print("\n2. Creating a new file...")
    result = await agent.client_tools.tools["create_markdown_file"]({
        "filename": "example_notes.md",
        "content": "# Example Notes\n\nThis is a test file created by the voice agent.\n\n## Features\n- File creation\n- Content management\n- Voice integration"
    })
    print(f"   Result: {result}")
    
    # Example 3: Read the file
    print("\n3. Reading the created file...")
    result = await agent.client_tools.tools["read_markdown_file"]({
        "filename": "example_notes.md"
    })
    print(f"   Result: {result}")
    
    # Example 4: Update the file
    print("\n4. Updating the file...")
    result = await agent.client_tools.tools["update_markdown_file"]({
        "filename": "example_notes.md",
        "content": "# Example Notes - Updated\n\nThis file has been updated by the voice agent.\n\n## Features\n- File creation\n- Content management\n- Voice integration\n- File updates\n\n## New Section\nAdded this section to demonstrate updates."
    })
    print(f"   Result: {result}")

async def example_script_operations():
    """Example of script operations through the voice agent"""
    print("\n📜 Example: Script Operations")
    print("-" * 30)
    
    # Initialize agent
    load_dotenv()
    agent = VoiceAgent(
        agent_id=os.getenv("ELEVENLABS_AGENT_ID"),
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )
    
    # Setup tools
    agent.setup_tools()
    
    # Example 1: List scripts
    print("1. Listing voice scripts...")
    result = await agent.client_tools.tools["list_voice_scripts"]({})
    print(f"   Result: {result}")
    
    # Example 2: Create a new script
    print("\n2. Creating a new voice script...")
    result = await agent.client_tools.tools["create_voice_script"]({
        "filename": "example_script.txt",
        "content": """# Example Voice Script

You are a helpful assistant for demonstrating voice agent capabilities.

## Instructions
1. Greet users warmly
2. Explain your file and script management capabilities
3. Help users with their requests
4. Be patient and clear in your responses

## Key Features
- File operations (create, read, update, delete)
- Script management
- Natural language processing
- Voice interaction

Remember to speak clearly and provide helpful feedback."""
    })
    print(f"   Result: {result}")
    
    # Example 3: Get the script
    print("\n3. Retrieving the created script...")
    result = await agent.client_tools.tools["get_voice_script"]({
        "filename": "example_script.txt"
    })
    print(f"   Result: {result}")

async def example_voice_conversation():
    """Example of starting a voice conversation"""
    print("\n🎤 Example: Voice Conversation")
    print("-" * 30)
    
    # Initialize agent
    load_dotenv()
    agent = VoiceAgent(
        agent_id=os.getenv("ELEVENLABS_AGENT_ID"),
        api_key=os.getenv("ELEVENLABS_API_KEY")
    )
    
    print("Starting voice conversation...")
    print("Note: This will start actual voice interaction.")
    print("Press Ctrl+C to stop.")
    
    try:
        # Start conversation
        agent.start_conversation()
    except KeyboardInterrupt:
        print("\nStopping conversation...")
        agent.end_conversation()

def main():
    """Main example function"""
    print("🚀 ElevenLabs Voice Agent Examples")
    print("=" * 50)
    
    # Check environment
    load_dotenv()
    if not os.getenv("ELEVENLABS_API_KEY") or not os.getenv("ELEVENLABS_AGENT_ID"):
        print("❌ Please configure ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID in .env file")
        return
    
    print("Choose an example to run:")
    print("1. File Operations Example")
    print("2. Script Operations Example")
    print("3. Voice Conversation Example")
    print("4. Run All Examples")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        asyncio.run(example_file_operations())
    elif choice == "2":
        asyncio.run(example_script_operations())
    elif choice == "3":
        asyncio.run(example_voice_conversation())
    elif choice == "4":
        print("Running all examples...")
        asyncio.run(example_file_operations())
        asyncio.run(example_script_operations())
        print("\nSkipping voice conversation example (requires user interaction)")
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
