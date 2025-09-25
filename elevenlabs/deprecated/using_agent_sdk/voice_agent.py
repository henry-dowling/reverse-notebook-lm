#!/usr/bin/env python3
"""
Voice Agent using ElevenLabs Conversational AI with Tools Integration
This agent can use file operations and script loading tools during conversations.
"""

import asyncio
import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ClientTools
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Load environment variables
load_dotenv()

class VoiceAgent:
    """Voice agent with tools integration for file operations and script management"""
    
    def __init__(self, agent_id: str, api_key: Optional[str] = None):
        """
        Initialize the voice agent
        
        Args:
            agent_id: ElevenLabs agent ID
            api_key: ElevenLabs API key (optional, will use env var if not provided)
        """
        self.agent_id = agent_id
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=self.api_key)
        self.audio_interface = DefaultAudioInterface()
        self.conversation = None
        self.client_tools = None
        self.base_url = "http://localhost:8001"  # FastAPI server URL
        
        # Load system prompt with dynamic variables
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load system prompt from file and update dynamic variables"""
        try:
            # Read the system prompt file
            with open("system_prompt.md", "r", encoding="utf-8") as f:
                prompt = f.read()
            
            # Update dynamic variables using scripts tool
            updated_prompt = self._update_dynamic_variables(prompt)
            return updated_prompt
            
        except FileNotFoundError:
            # Fallback system prompt if file doesn't exist
            return """You are a helpful voice assistant with access to file operations and script management tools.

You can:
- Create, read, update, and delete markdown files
- Load and manage interactive scripts
- Help users with various tasks using your available tools

Always be helpful, clear, and professional in your responses."""
    
    def _update_dynamic_variables(self, prompt: str) -> str:
        """Update dynamic variables in the system prompt using available scripts"""
        try:
            # Get available scripts to update the prompt
            response = requests.get(f"{self.base_url}/scripts")
            if response.status_code == 200:
                scripts = response.json()
                script_list = ", ".join(scripts) if scripts else "None available"
                
                # Replace placeholder with actual script list
                updated_prompt = prompt.replace("{{AVAILABLE_SCRIPTS}}", script_list)
                return updated_prompt
            else:
                return prompt.replace("{{AVAILABLE_SCRIPTS}}", "Unable to retrieve")
                
        except Exception as e:
            print(f"Warning: Could not update dynamic variables: {e}")
            return prompt.replace("{{AVAILABLE_SCRIPTS}}", "Error retrieving scripts")
    
    def _create_file_tool(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Create a file operation tool function"""
        async def file_operation_tool(params: Dict[str, Any]) -> str:
            try:
                # Map tool parameters to API call
                if operation == "list_files":
                    response = requests.get(f"{self.base_url}/workspace/files")
                elif operation == "read_file":
                    filename = params.get("filename", "output.md")
                    response = requests.get(f"{self.base_url}/workspace/files/{filename}")
                elif operation == "create_file":
                    filename = params.get("filename", "output.md")
                    content = params.get("content", "")
                    response = requests.post(
                        f"{self.base_url}/workspace/files/{filename}",
                        json={"content": content}
                    )
                elif operation == "update_file":
                    filename = params.get("filename", "output.md")
                    content = params.get("content", "")
                    response = requests.put(
                        f"{self.base_url}/workspace/files/{filename}",
                        json={"content": content}
                    )
                elif operation == "delete_file":
                    filename = params.get("filename", "output.md")
                    response = requests.delete(f"{self.base_url}/workspace/files/{filename}")
                elif operation == "edit_with_description":
                    filename = params.get("filename", "output.md")
                    description = params.get("description", "")
                    response = requests.put(
                        f"{self.base_url}/workspace/files/{filename}/edit",
                        json={"description": description}
                    )
                else:
                    return f"Unknown file operation: {operation}"
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return f"Success: {json.dumps(result, indent=2)}"
                else:
                    return f"Error: {response.status_code} - {response.text}"
                    
            except Exception as e:
                return f"Error performing file operation: {str(e)}"
        
        return file_operation_tool
    
    def _create_script_tool(self, operation: str) -> Dict[str, Any]:
        """Create a script operation tool function"""
        async def script_operation_tool(params: Dict[str, Any]) -> str:
            try:
                if operation == "list_scripts":
                    response = requests.get(f"{self.base_url}/scripts")
                elif operation == "get_script":
                    filename = params.get("filename", "")
                    response = requests.get(f"{self.base_url}/scripts/{filename}")
                elif operation == "create_script":
                    filename = params.get("filename", "")
                    content = params.get("content", "")
                    response = requests.post(
                        f"{self.base_url}/scripts/{filename}",
                        json={"content": content}
                    )
                elif operation == "update_script":
                    filename = params.get("filename", "")
                    content = params.get("content", "")
                    response = requests.put(
                        f"{self.base_url}/scripts/{filename}",
                        json={"content": content}
                    )
                elif operation == "delete_script":
                    filename = params.get("filename", "")
                    response = requests.delete(f"{self.base_url}/scripts/{filename}")
                else:
                    return f"Unknown script operation: {operation}"
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return f"Success: {json.dumps(result, indent=2)}"
                else:
                    return f"Error: {response.status_code} - {response.text}"
                    
            except Exception as e:
                return f"Error performing script operation: {str(e)}"
        
        return script_operation_tool
    
    def setup_tools(self):
        """Set up all available tools for the voice agent"""
        self.client_tools = ClientTools()
        
        # File operation tools
        self.client_tools.register(
            "list_markdown_files", 
            self._create_file_tool("list_files"),
            is_async=True
        )
        
        self.client_tools.register(
            "read_markdown_file",
            self._create_file_tool("read_file"),
            is_async=True
        )
        
        self.client_tools.register(
            "create_markdown_file",
            self._create_file_tool("create_file"),
            is_async=True
        )
        
        self.client_tools.register(
            "update_markdown_file",
            self._create_file_tool("update_file"),
            is_async=True
        )
        
        self.client_tools.register(
            "delete_markdown_file",
            self._create_file_tool("delete_file"),
            is_async=True
        )
        
        self.client_tools.register(
            "edit_file_with_description",
            self._create_file_tool("edit_with_description"),
            is_async=True
        )
        
        # Script operation tools
        self.client_tools.register(
            "list_voice_scripts",
            self._create_script_tool("list_scripts"),
            is_async=True
        )
        
        self.client_tools.register(
            "get_voice_script",
            self._create_script_tool("get_script"),
            is_async=True
        )
        
        self.client_tools.register(
            "create_voice_script",
            self._create_script_tool("create_script"),
            is_async=True
        )
        
        self.client_tools.register(
            "update_voice_script",
            self._create_script_tool("update_script"),
            is_async=True
        )
        
        self.client_tools.register(
            "delete_voice_script",
            self._create_script_tool("delete_script"),
            is_async=True
        )
        
        print("✅ All tools registered successfully")
    
    def start_conversation(self):
        """Start the voice conversation"""
        if not self.client_tools:
            self.setup_tools()
        
        # Create conversation with tools
        self.conversation = Conversation(
            client=self.client,
            agent_id=self.agent_id,
            requires_auth=True,
            audio_interface=self.audio_interface,
            client_tools=self.client_tools
        )
        
        print("🎤 Starting voice conversation...")
        print("💡 You can now speak to the agent. Say 'help' to see available commands.")
        print("🔧 The agent has access to file operations and script management tools.")
        print("⏹️  Press Ctrl+C to stop the conversation.")
        
        try:
            # Start the conversation session
            self.conversation.start_session()
            
            # Keep the conversation running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping conversation...")
            self.end_conversation()
        except Exception as e:
            print(f"❌ Error during conversation: {e}")
            self.end_conversation()
    
    def end_conversation(self):
        """End the voice conversation"""
        if self.conversation:
            self.conversation.end_session()
            print("✅ Conversation ended")
    
    async def test_tools(self):
        """Test all registered tools"""
        print("🧪 Testing tools...")
        
        # Test file operations
        try:
            result = await self.client_tools.tools["list_markdown_files"]({})
            print(f"📁 List files: {result}")
        except Exception as e:
            print(f"❌ List files error: {e}")
        
        # Test script operations
        try:
            result = await self.client_tools.tools["list_voice_scripts"]({})
            print(f"📜 List scripts: {result}")
        except Exception as e:
            print(f"❌ List scripts error: {e}")
        
        print("✅ Tool testing completed")

def main():
    """Main function to run the voice agent"""
    # Check for required environment variables
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ Error: ELEVENLABS_API_KEY not found in environment variables.")
        print("Please add your ElevenLabs API key to the .env file:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return
    
    # You need to create an agent in ElevenLabs and get its ID
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    if not agent_id:
        print("❌ Error: ELEVENLABS_AGENT_ID not found in environment variables.")
        print("Please create an agent in ElevenLabs and add its ID to the .env file:")
        print("ELEVENLABS_AGENT_ID=your_agent_id_here")
        return
    
    # Create and start the voice agent
    agent = VoiceAgent(agent_id=agent_id)
    
    # Test tools first
    asyncio.run(agent.test_tools())
    
    # Start the conversation
    agent.start_conversation()

if __name__ == "__main__":
    main()
