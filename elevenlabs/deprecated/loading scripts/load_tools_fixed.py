#!/usr/bin/env python3
"""
Fixed script to automatically load all FastAPI tools into ElevenLabs.
This script addresses the schema validation errors from the previous version.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
BASE_URL = "https://allegory.ngrok.app"  # Your FastAPI server URL
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/convai/tools"

def create_tool(tool_config):
    """Create a tool in ElevenLabs using the API"""
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(ELEVENLABS_API_URL, headers=headers, json=tool_config)
    
    if response.status_code in [200, 201]:
        print(f"✅ Successfully created tool: {tool_config['tool_config']['name']}")
        return response.json()
    else:
        print(f"❌ Failed to create tool: {tool_config['tool_config']['name']}")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def get_tool_configs():
    """Define all tool configurations with fixed schemas"""
    tools = []
    
    # Simple GET tools without parameters
    simple_tools = [
        {
            "name": "list_markdown_files",
            "description": "Get a list of all markdown files in the workspace. Use this when the user wants to see what markdown files are available.",
            "url": f"{BASE_URL}/workspace/files"
        },
        {
            "name": "list_voice_scripts", 
            "description": "Get a list of all voice agent instruction script files. Use when user wants to see available voice scripts.",
            "url": f"{BASE_URL}/scripts"
        }
    ]
    
    for tool in simple_tools:
        tools.append({
            "tool_config": {
                "type": "webhook",
                "name": tool["name"],
                "description": tool["description"],
                "webhook": {
                    "url": tool["url"],
                    "method": "GET",
                    "api_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        })
    
    # Tools with path parameters
    path_param_tools = [
        {
            "name": "read_markdown_file",
            "description": "Read the content of a specific markdown file. Ask the user for the filename if not provided.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}",
            "method": "GET",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the markdown file (with or without .md extension)"
                }
            }
        },
        {
            "name": "delete_markdown_file",
            "description": "Delete a markdown file from the workspace. Ask for the filename to delete.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}",
            "method": "DELETE",
            "path_params": {
                "filename": {
                    "type": "string", 
                    "description": "Name of the markdown file to delete"
                }
            }
        },
        {
            "name": "get_file_lines",
            "description": "Get all lines of a markdown file with line numbers for editing. Useful before editing specific lines.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}/lines",
            "method": "GET",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the markdown file"
                }
            }
        },
        {
            "name": "get_voice_script",
            "description": "Retrieve the content of a specific voice agent instruction script. Ask for the script filename.",
            "url": f"{BASE_URL}/scripts/{{filename}}",
            "method": "GET", 
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the script file including extension (.txt or .md)"
                }
            }
        },
        {
            "name": "delete_voice_script",
            "description": "Delete a voice agent instruction script. Ask for the script filename to delete.",
            "url": f"{BASE_URL}/scripts/{{filename}}",
            "method": "DELETE",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the script file to delete"
                }
            }
        }
    ]
    
    for tool in path_param_tools:
        tools.append({
            "tool_config": {
                "type": "webhook",
                "name": tool["name"],
                "description": tool["description"],
                "webhook": {
                    "url": tool["url"],
                    "method": tool["method"],
                    "api_schema": {
                        "type": "object",
                        "properties": tool["path_params"],
                        "required": list(tool["path_params"].keys())
                    }
                }
            }
        })
    
    # Tools with path parameters AND request body
    body_tools = [
        {
            "name": "create_markdown_file",
            "description": "Create a new markdown file with specified content. Ask the user for filename and content.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}",
            "method": "POST",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the markdown file to create"
                }
            },
            "request_body": {
                "content": {
                    "type": "string",
                    "description": "The markdown content for the file"
                }
            }
        },
        {
            "name": "update_markdown_file",
            "description": "Update the entire content of an existing markdown file. Ask for filename and new content.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}",
            "method": "PUT",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the markdown file to update"
                }
            },
            "request_body": {
                "content": {
                    "type": "string",
                    "description": "The new markdown content"
                }
            }
        },
        {
            "name": "edit_file_line",
            "description": "Edit a specific line in a markdown file by line number. Ask for filename, line number, and new content.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}/lines/{{line_number}}",
            "method": "PUT",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the markdown file"
                },
                "line_number": {
                    "type": "integer", 
                    "description": "Line number to edit (1-based)"
                }
            },
            "request_body": {
                "line_number": {
                    "type": "integer",
                    "description": "Line number to edit"
                },
                "new_content": {
                    "type": "string",
                    "description": "The new content for this line"
                }
            }
        },
        {
            "name": "edit_with_description",
            "description": "Edit a markdown file using natural language description (AI-powered). Ask for filename and description of changes.",
            "url": f"{BASE_URL}/workspace/files/{{filename}}/edit",
            "method": "PUT",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the markdown file to edit"
                }
            },
            "request_body": {
                "description": {
                    "type": "string",
                    "description": "Natural language description of how to edit the file"
                }
            }
        },
        {
            "name": "create_voice_script",
            "description": "Create a new voice agent instruction script. Ask for filename and the instruction content.",
            "url": f"{BASE_URL}/scripts/{{filename}}",
            "method": "POST",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the script file to create"
                }
            },
            "request_body": {
                "content": {
                    "type": "string",
                    "description": "The voice agent instruction content"
                }
            }
        },
        {
            "name": "update_voice_script",
            "description": "Update an existing voice agent instruction script. Ask for filename and updated content.",
            "url": f"{BASE_URL}/scripts/{{filename}}",
            "method": "PUT",
            "path_params": {
                "filename": {
                    "type": "string",
                    "description": "Name of the script file to update"
                }
            },
            "request_body": {
                "content": {
                    "type": "string",
                    "description": "The updated voice agent instruction content"
                }
            }
        }
    ]
    
    for tool in body_tools:
        # Combine path params and request body in api_schema properties
        all_properties = {}
        all_required = []
        
        if "path_params" in tool:
            all_properties.update(tool["path_params"])
            all_required.extend(list(tool["path_params"].keys()))
        
        if "request_body" in tool:
            all_properties.update(tool["request_body"])
            all_required.extend(list(tool["request_body"].keys()))
        
        tools.append({
            "tool_config": {
                "type": "webhook", 
                "name": tool["name"],
                "description": tool["description"],
                "webhook": {
                    "url": tool["url"],
                    "method": tool["method"],
                    "api_schema": {
                        "type": "object",
                        "properties": all_properties,
                        "required": all_required
                    }
                }
            }
        })
    
    return tools

def main():
    """Main function to load all tools into ElevenLabs"""
    if not ELEVENLABS_API_KEY:
        print("❌ Error: ELEVENLABS_API_KEY not found in environment variables.")
        print("Please add your ElevenLabs API key to the .env file:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return
    
    print("🚀 Loading all 13 tools into ElevenLabs (Fixed Version)...")
    print(f"📡 FastAPI Server: {BASE_URL}")
    print(f"🎯 ElevenLabs API: {ELEVENLABS_API_URL}")
    print("-" * 50)
    
    tools = get_tool_configs()
    created_tools = []
    failed_tools = []
    
    for i, tool in enumerate(tools, 1):
        tool_name = tool['tool_config']['name']
        print(f"[{i}/13] Creating: {tool_name}")
        result = create_tool(tool)
        
        if result:
            created_tools.append(tool_name)
        else:
            failed_tools.append(tool_name)
    
    print("-" * 50)
    print(f"✅ Successfully created {len(created_tools)} tools")
    print(f"❌ Failed to create {len(failed_tools)} tools")
    
    if failed_tools:
        print("\nFailed tools:")
        for tool in failed_tools:
            print(f"  - {tool}")
    
    if created_tools:
        print(f"\nSuccessfully created tools:")
        for tool in created_tools:
            print(f"  - {tool}")
    
    print(f"\n🎉 Tool loading completed!")
    print(f"You can now use the {len(created_tools)} working tools in your ElevenLabs voice agent.")

if __name__ == "__main__":
    main()