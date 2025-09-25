#!/usr/bin/env python3
"""
Script to automatically load all FastAPI tools into ElevenLabs using the official SDK.
This script creates all 13 tools in your ElevenLabs workspace.
"""

import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, ToolRequestModel
from elevenlabs.types import (
    ToolRequestModelToolConfig_Webhook,
    WebhookToolConfigInput,
    WebhookToolApiSchemaConfigInput,
    WebhookToolApiSchemaConfigInputMethod
)

# Load environment variables
load_dotenv()

# Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
BASE_URL = "https://allegory.ngrok.app"  # Your FastAPI server URL

def create_tool(client, name, description, url, method="GET", path_params=None, request_body=None):
    """Create a tool in ElevenLabs using the SDK"""
    try:
        # Build API schema
        api_schema_config = {
            "url": url,
            "method": method
        }
        
        # Add path parameters schema if needed
        if path_params:
            api_schema_config["path_params_schema"] = {
                "type": "object",
                "properties": path_params,
                "required": list(path_params.keys())
            }
        
        # Add request body schema if needed
        if request_body:
            api_schema_config["request_body_schema"] = {
                "type": "object",
                "properties": request_body,
                "required": list(request_body.keys())
            }
        
        # Create the tool request model
        tool_request = ToolRequestModel(
            tool_config=ToolRequestModelToolConfig_Webhook(
                name=name,
                description=description,
                api_schema=WebhookToolApiSchemaConfigInput(**api_schema_config),
                webhook=WebhookToolConfigInput(
                    name=name,
                    description=description,
                    api_schema=WebhookToolApiSchemaConfigInput(**api_schema_config)
                )
            )
        )
        
        result = client.conversational_ai.tools.create(request=tool_request)
        print(f"✅ Successfully created tool: {name}")
        return result
    except Exception as e:
        print(f"❌ Failed to create tool: {name}")
        print(f"   Error: {str(e)}")
        return None

def get_tool_configs():
    """Define all tool configurations with proper schemas"""
    tools = [
        # Markdown file management tools
        {
            "name": "list_markdown_files",
            "description": "Get a list of all markdown files in the workspace. Use this when the user wants to see what markdown files are available.",
            "url": f"{BASE_URL}/workspace/files",
            "method": "GET"
        },
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
        
        # Voice script management tools
        {
            "name": "list_voice_scripts",
            "description": "Get a list of all voice agent instruction script files. Use when user wants to see available voice scripts.",
            "url": f"{BASE_URL}/scripts",
            "method": "GET"
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
    
    return tools

def main():
    """Main function to load all tools into ElevenLabs using the SDK"""
    if not ELEVENLABS_API_KEY:
        print("❌ Error: ELEVENLABS_API_KEY not found in environment variables.")
        print("Please add your ElevenLabs API key to the .env file:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return
    
    print("🚀 Loading tools into ElevenLabs using SDK...")
    print(f"📡 FastAPI Server: {BASE_URL}")
    print("-" * 50)
    
    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    tools = get_tool_configs()
    created_tools = []
    failed_tools = []
    
    for i, tool in enumerate(tools, 1):
        name = tool["name"]
        print(f"[{i}/13] Creating: {name}")
        
        result = create_tool(
            client=client,
            name=tool["name"],
            description=tool["description"],
            url=tool["url"],
            method=tool["method"],
            path_params=tool.get("path_params"),
            request_body=tool.get("request_body")
        )
        
        if result:
            created_tools.append(name)
        else:
            failed_tools.append(name)
    
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
    print(f"You can now use these tools in your ElevenLabs voice agent.")

if __name__ == "__main__":
    main()