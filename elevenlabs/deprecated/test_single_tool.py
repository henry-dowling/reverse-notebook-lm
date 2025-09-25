#!/usr/bin/env python3
"""Test script to create a single tool and debug the API format"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
BASE_URL = "https://allegory.ngrok.app"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/convai/tools"

def test_single_tool():
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test with the correct ElevenLabs API schema format
    tool_config = {
        "tool_config": {
            "type": "webhook",
            "name": "list_files",
            "description": "Get a list of all markdown files",
            "api_schema": {
                "url": f"{BASE_URL}/workspace/files",
                "method": "GET"
            }
        }
    }
    
    print("Testing tool creation with ElevenLabs API...")
    print(f"Config: {json.dumps(tool_config, indent=2)}")
    
    response = requests.post(ELEVENLABS_API_URL, headers=headers, json=tool_config)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_single_tool()