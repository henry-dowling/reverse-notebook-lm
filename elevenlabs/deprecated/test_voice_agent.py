#!/usr/bin/env python3
"""
Test script for the ElevenLabs Voice Agent
This script tests the voice agent functionality without requiring voice input.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from voice_agent import VoiceAgent

def test_agent_initialization():
    """Test agent initialization"""
    print("🧪 Testing agent initialization...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Check for required environment variables
        api_key = os.getenv("ELEVENLABS_API_KEY")
        agent_id = os.getenv("ELEVENLABS_AGENT_ID")
        
        if not api_key or api_key == "your_elevenlabs_api_key_here":
            print("❌ ELEVENLABS_API_KEY not configured")
            return False
        
        if not agent_id or agent_id == "your_agent_id_here":
            print("❌ ELEVENLABS_AGENT_ID not configured")
            return False
        
        # Initialize agent
        agent = VoiceAgent(agent_id=agent_id, api_key=api_key)
        print("✅ Agent initialized successfully")
        return agent
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_system_prompt_loading():
    """Test system prompt loading"""
    print("🧪 Testing system prompt loading...")
    
    try:
        agent = VoiceAgent(agent_id="test", api_key="test")
        prompt = agent._load_system_prompt()
        
        if prompt and len(prompt) > 100:
            print("✅ System prompt loaded successfully")
            print(f"   Prompt length: {len(prompt)} characters")
            return True
        else:
            print("❌ System prompt too short or empty")
            return False
            
    except Exception as e:
        print(f"❌ System prompt loading failed: {e}")
        return False

def test_dynamic_variable_update():
    """Test dynamic variable updating"""
    print("🧪 Testing dynamic variable update...")
    
    try:
        agent = VoiceAgent(agent_id="test", api_key="test")
        
        # Test prompt with placeholder
        test_prompt = "Available scripts: {{AVAILABLE_SCRIPTS}}"
        updated_prompt = agent._update_dynamic_variables(test_prompt)
        
        if "{{AVAILABLE_SCRIPTS}}" not in updated_prompt:
            print("✅ Dynamic variable updated successfully")
            print(f"   Updated prompt: {updated_prompt}")
            return True
        else:
            print("❌ Dynamic variable not updated")
            return False
            
    except Exception as e:
        print(f"❌ Dynamic variable update failed: {e}")
        return False

async def test_tool_setup():
    """Test tool setup"""
    print("🧪 Testing tool setup...")
    
    try:
        agent = VoiceAgent(agent_id="test", api_key="test")
        agent.setup_tools()
        
        if agent.client_tools and len(agent.client_tools.tools) > 0:
            print("✅ Tools setup successfully")
            print(f"   Registered tools: {len(agent.client_tools.tools)}")
            for tool_name in agent.client_tools.tools.keys():
                print(f"     - {tool_name}")
            return True
        else:
            print("❌ No tools registered")
            return False
            
    except Exception as e:
        print(f"❌ Tool setup failed: {e}")
        return False

async def test_tool_execution():
    """Test tool execution"""
    print("🧪 Testing tool execution...")
    
    try:
        agent = VoiceAgent(agent_id="test", api_key="test")
        agent.setup_tools()
        
        # Test a simple tool call
        if "list_markdown_files" in agent.client_tools.tools:
            result = await agent.client_tools.tools["list_markdown_files"]({})
            print("✅ Tool execution successful")
            print(f"   Result: {result[:100]}..." if len(result) > 100 else f"   Result: {result}")
            return True
        else:
            print("❌ Tool not found")
            return False
            
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        return False

def test_backend_connection():
    """Test backend connection"""
    print("🧪 Testing backend connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:8001/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend connection successful")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        print("   Make sure the FastAPI backend is running on http://localhost:8001")
        return False

async def main():
    """Main test function"""
    print("🧪 ElevenLabs Voice Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("System Prompt Loading", test_system_prompt_loading),
        ("Dynamic Variable Update", test_dynamic_variable_update),
        ("Backend Connection", test_backend_connection),
        ("Agent Initialization", test_agent_initialization),
        ("Tool Setup", test_tool_setup),
        ("Tool Execution", test_tool_execution),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The voice agent is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
