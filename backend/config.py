import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-realtime-preview-2024-12-17"
OPENAI_VOICE = os.getenv("DEFAULT_VOICE", "verse")

# WebSocket Configuration
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", "localhost")
WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8765"))

# File System Configuration
WORKING_DIRECTORY = os.getenv("WORKING_DIRECTORY", "./workspace")
DEFAULT_OUTPUT_FILE = "output.md"

# Realtime API Configuration
REALTIME_CONFIG = {
    "model": OPENAI_MODEL,
    "voice": OPENAI_VOICE,
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16",
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500
    },
    "tools": [
        {
            "type": "function",
            "name": "load_script",
            "description": "Load an interactive script to guide the conversation",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name of the script to load (e.g., 'blog_writer', 'improv_game')"
                    }
                },
                "required": ["script_name"]
            }
        },
        {
            "type": "function",
            "name": "file_operation",
            "description": "Perform operations on local markdown files",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["create", "read", "write", "append", "insert", "replace", "save_as"],
                        "description": "The type of file operation to perform"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Name of the markdown file to operate on",
                        "default": "output.md"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content for write operations"
                    },
                    "line_number": {
                        "type": "integer",
                        "description": "Line number for insert operations"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Pattern to search for in replace operations"
                    },
                    "replacement": {
                        "type": "string",
                        "description": "Replacement text for replace operations"
                    }
                },
                "required": ["operation"]
            }
        }
    ]
}

# Available Scripts
AVAILABLE_SCRIPTS = [
    "blog_writer",
    "improv_game", 
    "email_workshop",
    "brainstorm_session",
    "interview_prep"
]