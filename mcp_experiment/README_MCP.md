# MCP Server for Reverse Notebook LM

This MCP (Model Context Protocol) server provides tools for retrieving interactive scripts and editing files within the Reverse Notebook LM system, built using the modern FastMCP architecture.

## Architecture

This implementation uses the modern **FastMCP** framework, following the latest Python SDK best practices with:
- `@mcp.tool()` and `@mcp.resource()` decorators
- Automatic schema generation from type hints
- Structured error handling with custom exception classes
- Enhanced type safety with Pydantic models
- Production-ready HTTP wrapper with security features

## Features

### Script Management Tools
- **list_scripts**: List all available interactive scripts with descriptions
- **get_script**: Get detailed information about a specific script
- **load_script**: Load and activate an interactive script for execution
- **get_script_progress**: Get current script progress and stage information
- **advance_script_stage**: Advance to the next stage of the current script
- **reset_script**: Reset the current script to the beginning
- **clear_script**: Clear the current active script

### File Operations Tools
- **read_file**: Read the contents of a markdown file from the workspace
- **write_file**: Write content to a markdown file (overwrites existing content)
- **append_file**: Append content to an existing markdown file
- **insert_file_content**: Insert content at a specific line number
- **edit_file_lines**: Edit specific lines of a file by replacing content at specified line numbers
- **replace_file_content**: Replace all occurrences of a regex pattern in a file
- **list_files**: List all markdown files in the workspace directory
- **get_file_info**: Get detailed information about a specific file
- **create_file**: Create a new markdown file with optional initial content
- **create_backup**: Create a timestamped backup of a file

### Resources (Read-Only Data Access)
- **scripts://list**: List of available scripts
- **scripts://{script_name}**: Detailed script information
- **files://list**: List of available files
- **files://{filename}**: File content

## Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. The server files are ready to run (no additional setup needed)

## Usage

### Running the FastMCP Server (Stdio Transport)

```bash
cd backend
python mcp_server.py
```

### Running the HTTP Wrapper Server

```bash
# Basic HTTP server
python http_mcp_server.py --host 0.0.0.0 --port 8000

# With API key authentication
python http_mcp_server.py --api-key your-secret-key

# With specific CORS origins
python http_mcp_server.py --origins "https://yourdomain.com,https://otherdomain.com"

# Production configuration
export MCP_API_KEY="your-secret-key"
export ALLOWED_ORIGINS="https://your-production-domain.com"
python http_mcp_server.py --host 127.0.0.1 --port 8000
```

### API Documentation

When running the HTTP server, comprehensive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Testing the Server

Run the comprehensive test to verify all functionality:
```bash
cd backend
python test_mcp_complete.py
```

### Integration with MCP Clients

To use this server with MCP clients like Claude Desktop, add the following configuration:

**For Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "reverse-notebook-lm": {
      "command": "python",
      "args": ["/path/to/reverse-notebook-lm/backend/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/reverse-notebook-lm/backend"
      }
    }
  }
}
```

**For HTTP-based integrations**, use the HTTP endpoints at `http://localhost:8000`

## Available Scripts

The server includes these interactive scripts:

1. **blog_writer**: Blog Post Writing Assistant - Helps create engaging blog posts
2. **improv_game**: Yes, And... Improv Game - Play collaborative storytelling games  
3. **email_workshop**: Email Writing Workshop - Craft effective emails through guided practice
4. **brainstorm_session**: Creative Brainstorming Session - Generate and develop ideas
5. **interview_prep**: Interview Preparation Coach - Practice interviews with real-time feedback

## HTTP Endpoints

### Core MCP Endpoints
- `GET /` - Server information with capabilities
- `GET /health` - Health check with uptime
- `GET /tools` - List all available tools
- `POST /tools/call` - Execute any tool
- `GET /resources` - List available resources
- `POST /resources/get` - Access specific resource

### Legacy Compatibility
- `GET /scripts` - List scripts
- `GET /files` - List files

### Integration Endpoints  
- `GET /mcp/info` - MCP server metadata
- `POST /webhook/elevenlabs` - ElevenLabs voice integration

## Security Features

### Production Security
- **API Key Authentication**: Bearer token authentication via `MCP_API_KEY` env var
- **CORS Configuration**: Specific allowed origins (no wildcards)
- **Input Validation**: Comprehensive Pydantic model validation
- **Structured Error Handling**: Detailed error responses with appropriate HTTP status codes
- **File System Security**: Operations restricted to workspace directory

### Error Handling

The server provides structured error responses:
```json
{
  "success": false,
  "error": "Script 'nonexistent' not found", 
  "error_type": "ScriptNotFoundError",
  "detail": "Requested script was not found"
}
```

## File Operations

All file operations work with markdown files in the workspace directory (`./workspace/` by default). The server provides:

- Reading and writing files with full content management
- Line-specific insertions and edits
- Pattern-based replacements using regular expressions
- File metadata retrieval (size, modification time, etc.)
- Automatic backup creation with timestamps
- Comprehensive file listing and information

## Voice Integration

The HTTP server includes ElevenLabs webhook support for voice commands:
- "list scripts" - Lists available interactive scripts
- "load script [name]" - Loads a specific script (blog, improv, email, etc.)
- "read file" - Reads the current output file
- "script progress" - Shows current script progress
- "advance stage" - Advances to the next script stage

## Development

### Adding New Tools

```python
@mcp.tool()
def my_new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Description of what this tool does.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter with default
        
    Returns:
        Dictionary with operation results
    """
    return {"success": True, "result": "something"}
```

### Adding New Resources

```python
@mcp.resource("my_resource://{resource_id}")
def get_my_resource(resource_id: str) -> Any:
    """Resource providing specific data"""
    return some_data
```

The FastMCP framework automatically handles schema generation, validation, and documentation from your type hints and docstrings.

## Configuration Files

- `mcp_config.json` - MCP server configuration
- `claude_desktop_config.json` - Claude Desktop integration config

## Type Safety & Modern Features

- **Pydantic Models**: `ScriptInfo`, `ScriptProgress`, `FileInfo`, `LineEdit`
- **Custom Exceptions**: `MCPError`, `ValidationError`, `ScriptNotFoundError`, `FileOperationError`
- **Type Annotations**: Comprehensive type hints throughout
- **Automatic Documentation**: Generated from docstrings and type hints
- **Schema Validation**: Automatic request/response validation

This implementation provides a production-ready MCP server with modern architecture, comprehensive error handling, and security features suitable for both development and production environments.