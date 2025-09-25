#!/usr/bin/env python3
"""
Complete HTTP-based script to automatically load all 13 FastAPI tools into ElevenLabs.
Uses the exact schema format from ElevenLabs API documentation.
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
    """Create a tool in ElevenLabs using the HTTP API"""
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
    """Define all tool configurations using the exact ElevenLabs API schema"""
    tools = [
        # 1. List Markdown Files (GET, no parameters)
        {
            "tool_config": {
                "type": "webhook",
                "name": "list_markdown_files",
                "description": "Get a list of all markdown files in the workspace. Use this when the user wants to see what markdown files are available.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files",
                    "method": "GET",
                    "path_params_schema": {},
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 2. Read Markdown File (GET with path parameter)
        {
            "tool_config": {
                "type": "webhook",
                "name": "read_markdown_file",
                "description": "Read the content of a specific markdown file. Ask the user for the filename if not provided.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}",
                    "method": "GET",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file (with or without .md extension)"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 3. Create Markdown File (POST with path parameter and request body)
        {
            "tool_config": {
                "type": "webhook", 
                "name": "create_markdown_file",
                "description": "Create a new markdown file with specified content. Ask the user for filename and content.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}",
                    "method": "POST",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file to create"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_body_schema": {
                        "type": "object",
                        "description": "Request body for creating a markdown file",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The markdown content for the file"
                            }
                        },
                        "required": ["content"]
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 4. Update Markdown File (PUT with path parameter and request body)
        {
            "tool_config": {
                "type": "webhook",
                "name": "update_markdown_file",
                "description": "Update the entire content of an existing markdown file. Ask for filename and new content.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}",
                    "method": "PUT",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file to update"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_body_schema": {
                        "type": "object",
                        "description": "Request body for updating a markdown file",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The new markdown content"
                            }
                        },
                        "required": ["content"]
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 5. Delete Markdown File (DELETE with path parameter)
        {
            "tool_config": {
                "type": "webhook",
                "name": "delete_markdown_file",
                "description": "Delete a markdown file from the workspace. Ask for the filename to delete.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}",
                    "method": "DELETE",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file to delete"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 6. Get File Lines (GET with path parameter)
        {
            "tool_config": {
                "type": "webhook",
                "name": "get_file_lines",
                "description": "Get all lines of a markdown file with line numbers for editing. Useful before editing specific lines.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}/lines",
                    "method": "GET",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 7. Edit File Line (PUT with path parameters and request body)
        {
            "tool_config": {
                "type": "webhook",
                "name": "edit_file_line",
                "description": "Edit a specific line in a markdown file by line number. Ask for filename, line number, and new content.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}/lines/{{line_number}}",
                    "method": "PUT",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file"
                            },
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to edit (1-based)"
                            }
                        },
                        "required": ["filename", "line_number"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_body_schema": {
                        "type": "object",
                        "description": "Request body for editing a specific line",
                        "properties": {
                            "line_number": {
                                "type": "integer",
                                "description": "Line number to edit"
                            },
                            "new_content": {
                                "type": "string",
                                "description": "The new content for this line"
                            }
                        },
                        "required": ["line_number", "new_content"]
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 8. Edit with Description (AI-powered PUT with path parameter and request body)
        {
            "tool_config": {
                "type": "webhook",
                "name": "edit_with_description",
                "description": "Edit a markdown file using natural language description (AI-powered). Ask for filename and description of changes.",
                "response_timeout_secs": 30,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/workspace/files/{{filename}}/edit",
                    "method": "PUT",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the markdown file to edit"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_body_schema": {
                        "type": "object",
                        "description": "Request body for AI-powered editing",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Natural language description of how to edit the file"
                            }
                        },
                        "required": ["description"]
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 9. List Voice Scripts (GET, no parameters)
        {
            "tool_config": {
                "type": "webhook",
                "name": "list_voice_scripts",
                "description": "Get a list of all voice agent instruction script files. Use when user wants to see available voice scripts.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/scripts",
                    "method": "GET",
                    "path_params_schema": {},
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 10. Get Voice Script (GET with path parameter)
        {
            "tool_config": {
                "type": "webhook",
                "name": "get_voice_script",
                "description": "Retrieve the content of a specific voice agent instruction script. Ask for the script filename.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/scripts/{{filename}}",
                    "method": "GET",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the script file including extension (.txt or .md)"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 11. Create Voice Script (POST with path parameter and request body)
        {
            "tool_config": {
                "type": "webhook",
                "name": "create_voice_script",
                "description": "Create a new voice agent instruction script. Ask for filename and the instruction content.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/scripts/{{filename}}",
                    "method": "POST",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the script file to create"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_body_schema": {
                        "type": "object",
                        "description": "Request body for creating a voice script",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The voice agent instruction content"
                            }
                        },
                        "required": ["content"]
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 12. Update Voice Script (PUT with path parameter and request body)
        {
            "tool_config": {
                "type": "webhook",
                "name": "update_voice_script",
                "description": "Update an existing voice agent instruction script. Ask for filename and updated content.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/scripts/{{filename}}",
                    "method": "PUT",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the script file to update"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_body_schema": {
                        "type": "object",
                        "description": "Request body for updating a voice script",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The updated voice agent instruction content"
                            }
                        },
                        "required": ["content"]
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        },
        
        # 13. Delete Voice Script (DELETE with path parameter)
        {
            "tool_config": {
                "type": "webhook",
                "name": "delete_voice_script",
                "description": "Delete a voice agent instruction script. Ask for the script filename to delete.",
                "response_timeout_secs": 20,
                "disable_interruptions": False,
                "force_pre_tool_speech": False,
                "assignments": [],
                "api_schema": {
                    "url": f"{BASE_URL}/scripts/{{filename}}",
                    "method": "DELETE",
                    "path_params_schema": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the script file to delete"
                            }
                        },
                        "required": ["filename"]
                    },
                    "query_params_schema": {
                        "properties": {},
                        "required": []
                    },
                    "request_headers": {}
                },
                "dynamic_variables": {
                    "dynamic_variable_placeholders": {}
                }
            }
        }
    ]
    
    return tools

def main():
    """Main function to load all tools into ElevenLabs using HTTP API"""
    if not ELEVENLABS_API_KEY:
        print("❌ Error: ELEVENLABS_API_KEY not found in environment variables.")
        print("Please add your ElevenLabs API key to the .env file:")
        print("ELEVENLABS_API_KEY=your_api_key_here")
        return
    
    print("🚀 Loading all 13 tools into ElevenLabs using complete HTTP API...")
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
    if len(created_tools) == 13:
        print("🎊 ALL 13 TOOLS SUCCESSFULLY CREATED!")
        print("Your ElevenLabs voice agent now has full access to all markdown and voice script management tools.")
    else:
        print(f"You can now use the {len(created_tools)} working tools in your ElevenLabs voice agent.")

if __name__ == "__main__":
    main()