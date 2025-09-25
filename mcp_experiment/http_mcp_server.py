#!/usr/bin/env python3
"""
HTTP Server wrapper for FastMCP Server
Provides both MCP protocol and REST API endpoints for remote access with enhanced security
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Import our MCP server
from mcp_server import mcp, MCPError, ValidationError, ScriptNotFoundError, FileOperationError

# Security setup
security = HTTPBearer(auto_error=False)

# Get allowed origins from environment or use defaults
DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080", 
    "http://localhost:6274",  # MCP Inspector default port
    "https://elevenlabs.io",
    "https://app.elevenlabs.io"
]

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", ",".join(DEFAULT_ORIGINS)).split(",")
API_KEY = os.getenv("MCP_API_KEY")  # Optional API key for authentication

# Custom CORS middleware to handle dynamic origins (like ngrok URLs)
class DynamicCORSMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origins=None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or []
    
    def is_origin_allowed(self, origin):
        """Check if origin is allowed, including ngrok URLs and ElevenLabs"""
        if not origin:
            return False
            
        # Always allow localhost and common development ports
        if any(origin.startswith(prefix) for prefix in [
            "http://localhost:", "http://127.0.0.1:", "https://localhost:", "https://127.0.0.1:"
        ]):
            return True
            
        # Allow ElevenLabs domains
        if any(origin.startswith(prefix) for prefix in [
            "https://elevenlabs.io", "https://app.elevenlabs.io"
        ]):
            return True
            
        # Allow ngrok URLs
        if origin.startswith("https://") and ".ngrok" in origin:
            return True
            
        # Check against explicitly allowed origins
        return origin in self.allowed_origins
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        if request.method == "OPTIONS":
            response = Response()
            if self.is_origin_allowed(origin):
                response.headers["Access-Control-Allow-Origin"] = origin or "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        
        response = await call_next(request)
        
        if self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

# Initialize FastAPI app
app = FastAPI(
    title="Reverse Notebook LM HTTP MCP Server",
    description="HTTP wrapper for FastMCP server with enhanced security and type safety",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with dynamic origin support
app.add_middleware(DynamicCORSMiddleware, allowed_origins=ALLOWED_ORIGINS)

# Server startup time for uptime calculation
_startup_time = asyncio.get_event_loop().time()

# Enhanced Pydantic models for request/response
class ToolCallRequest(BaseModel):
    """Request model for tool calls"""
    name: str = Field(description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")

class ToolCallResponse(BaseModel):
    """Response model for tool calls"""
    success: bool = Field(description="Whether the operation succeeded")
    result: Any = Field(description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    error_type: Optional[str] = Field(None, description="Type of error that occurred")

class ResourceRequest(BaseModel):
    """Request model for resource access"""
    uri: str = Field(description="Resource URI to access")

class ServerInfo(BaseModel):
    """Server information model"""
    name: str
    version: str
    status: str
    type: str
    capabilities: List[str]
    endpoints: Dict[str, str]
    security_enabled: bool
    cors_origins: List[str]

class HealthStatus(BaseModel):
    """Health check response model"""
    status: str
    timestamp: float
    uptime: float
    version: str

# Authentication dependency (optional)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional authentication dependency"""
    if API_KEY and credentials:
        if credentials.credentials != API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
    return credentials.credentials if credentials else None

# Error handling middleware
@app.exception_handler(MCPError)
async def mcp_error_handler(request: Request, exc: MCPError):
    """Handle MCP-specific errors"""
    error_type = type(exc).__name__
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": str(exc),
            "error_type": error_type,
            "detail": "MCP operation failed"
        }
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "detail": "Input validation failed"
        }
    )

@app.exception_handler(ScriptNotFoundError)
async def script_not_found_handler(request: Request, exc: ScriptNotFoundError):
    """Handle script not found errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": str(exc),
            "error_type": "ScriptNotFoundError",
            "detail": "Requested script was not found"
        }
    )

@app.exception_handler(FileOperationError)
async def file_operation_error_handler(request: Request, exc: FileOperationError):
    """Handle file operation errors"""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": str(exc),
            "error_type": "FileOperationError",
            "detail": "File operation failed"
        }
    )

# Root endpoints
@app.get("/", response_model=ServerInfo)
async def root():
    """Root endpoint with comprehensive server information"""
    return ServerInfo(
        name="Reverse Notebook LM HTTP MCP Server",
        version="2.0.0",
        status="running",
        type="mcp_fastmcp_server",
        capabilities=[
            "script_management", 
            "file_operations", 
            "voice_integration",
            "resource_access",
            "structured_responses",
            "error_handling",
            "type_safety"
        ],
        endpoints={
            "tools": "/tools",
            "resources": "/resources",
            "call_tool": "/tools/call",
            "scripts": "/scripts", 
            "files": "/files",
            "mcp_info": "/mcp/info",
            "mcp_tools": "/mcp/tools",
            "health": "/health",
            "docs": "/docs"
        },
        security_enabled=API_KEY is not None,
        cors_origins=ALLOWED_ORIGINS
    )

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Enhanced health check endpoint"""
    current_time = asyncio.get_event_loop().time()
    return HealthStatus(
        status="healthy",
        timestamp=current_time,
        uptime=current_time - _startup_time,
        version="2.0.0"
    )

# MCP Tools endpoints
@app.get("/tools")
async def list_tools(user: Optional[str] = Depends(get_current_user)):
    """List all available MCP tools with enhanced metadata"""
    try:
        # Get tools from FastMCP server
        tools_info = []
        
        # Since FastMCP handles tool introspection differently, 
        # we'll provide a static list based on our defined tools
        available_tools = [
            {
                "name": "list_scripts",
                "description": "List all available interactive scripts with their descriptions",
                "category": "script_management",
                "parameters": {},
                "returns": "Dictionary with scripts list and metadata"
            },
            {
                "name": "get_script", 
                "description": "Get detailed information about a specific script",
                "category": "script_management",
                "parameters": {"script_name": {"type": "string", "required": True}},
                "returns": "Dictionary with script details"
            },
            {
                "name": "load_script",
                "description": "Load and activate an interactive script for execution", 
                "category": "script_management",
                "parameters": {"script_name": {"type": "string", "required": True}},
                "returns": "Dictionary with load status and initial instructions"
            },
            {
                "name": "get_script_progress",
                "description": "Get current progress and stage information for the active script",
                "category": "script_management", 
                "parameters": {},
                "returns": "ScriptProgress model with current state"
            },
            {
                "name": "advance_script_stage",
                "description": "Advance to the next stage of the currently active script",
                "category": "script_management",
                "parameters": {},
                "returns": "Dictionary with advancement status"
            },
            {
                "name": "reset_script",
                "description": "Reset the currently active script back to the beginning",
                "category": "script_management",
                "parameters": {},
                "returns": "Dictionary with reset status"
            },
            {
                "name": "clear_script",
                "description": "Clear the currently active script and return to idle state",
                "category": "script_management", 
                "parameters": {},
                "returns": "Dictionary with clear operation status"
            },
            {
                "name": "read_file",
                "description": "Read the contents of a markdown file from the workspace",
                "category": "file_operations",
                "parameters": {"filename": {"type": "string", "default": "output.md"}},
                "returns": "Dictionary with file contents and metadata"
            },
            {
                "name": "write_file",
                "description": "Write content to a markdown file, overwriting existing content",
                "category": "file_operations",
                "parameters": {
                    "content": {"type": "string", "required": True},
                    "filename": {"type": "string", "default": "output.md"}
                },
                "returns": "Dictionary with write operation status"
            },
            {
                "name": "append_file",
                "description": "Append content to an existing markdown file",
                "category": "file_operations", 
                "parameters": {
                    "content": {"type": "string", "required": True},
                    "filename": {"type": "string", "default": "output.md"}
                },
                "returns": "Dictionary with append operation status"
            },
            {
                "name": "list_files",
                "description": "List all markdown files in the workspace directory",
                "category": "file_operations",
                "parameters": {},
                "returns": "Dictionary with list of files and count"
            },
            {
                "name": "get_file_info",
                "description": "Get detailed information about a specific file",
                "category": "file_operations",
                "parameters": {"filename": {"type": "string", "required": True}},
                "returns": "FileInfo model with file metadata"
            },
            {
                "name": "create_file",
                "description": "Create a new markdown file with optional initial content",
                "category": "file_operations",
                "parameters": {
                    "filename": {"type": "string", "required": True},
                    "content": {"type": "string", "default": ""}
                },
                "returns": "Dictionary with creation status and file path"
            },
            {
                "name": "create_backup",
                "description": "Create a timestamped backup of a file",
                "category": "file_operations",
                "parameters": {"filename": {"type": "string", "required": True}},
                "returns": "Dictionary with backup operation status and path"
            }
        ]
        
        return {
            "success": True,
            "tools": available_tools,
            "count": len(available_tools),
            "categories": ["script_management", "file_operations"],
            "server_type": "FastMCP",
            "version": "2.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")

@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(
    request: ToolCallRequest, 
    user: Optional[str] = Depends(get_current_user)
):
    """Call any MCP tool by name with enhanced error handling"""
    try:
        # Import the actual tool functions from mcp_server
        from mcp_server import (
            list_scripts, get_script, load_script, get_script_progress,
            advance_script_stage, reset_script, clear_script,
            read_file, write_file, append_file, list_files,
            get_file_info, create_file, create_backup
        )
        
        # Map tool names to actual tool functions
        tool_mapping = {
            "list_scripts": lambda: list_scripts(),
            "get_script": lambda: get_script(**request.arguments),
            "load_script": lambda: load_script(**request.arguments),
            "get_script_progress": lambda: get_script_progress(),
            "advance_script_stage": lambda: advance_script_stage(),
            "reset_script": lambda: reset_script(),
            "clear_script": lambda: clear_script(),
            "read_file": lambda: read_file(**request.arguments),
            "write_file": lambda: write_file(**request.arguments),
            "append_file": lambda: append_file(**request.arguments),
            "list_files": lambda: list_files(),
            "get_file_info": lambda: get_file_info(**request.arguments),
            "create_file": lambda: create_file(**request.arguments),
            "create_backup": lambda: create_backup(**request.arguments),
        }
        
        if request.name not in tool_mapping:
            raise ValidationError(f"Unknown tool: {request.name}")
        
        # Execute the tool
        result = tool_mapping[request.name]()
        
        return ToolCallResponse(
            success=True,
            result=result,
            error=None
        )
        
    except (MCPError, ValidationError, ScriptNotFoundError, FileOperationError) as e:
        # These are handled by the exception handlers
        raise
    except Exception as e:
        return ToolCallResponse(
            success=False,
            result=None,
            error=str(e),
            error_type=type(e).__name__
        )

# Resource endpoints
@app.get("/resources")
async def list_resources(user: Optional[str] = Depends(get_current_user)):
    """List all available MCP resources"""
    return {
        "success": True,
        "resources": [
            {
                "uri": "scripts://list",
                "description": "List of available scripts",
                "type": "script_collection"
            },
            {
                "uri": "scripts://{script_name}",
                "description": "Detailed script information",
                "type": "script_details",
                "parameters": ["script_name"]
            },
            {
                "uri": "files://list", 
                "description": "List of available files",
                "type": "file_collection"
            },
            {
                "uri": "files://{filename}",
                "description": "File content", 
                "type": "file_content",
                "parameters": ["filename"]
            }
        ],
        "count": 4
    }

@app.post("/resources/get")
async def get_resource(
    request: ResourceRequest,
    user: Optional[str] = Depends(get_current_user)
):
    """Get a specific resource by URI"""
    try:
        # Parse the resource URI and call appropriate resource function
        uri = request.uri
        
        if uri == "scripts://list":
            result = mcp.call_resource("scripts://list")
        elif uri.startswith("scripts://"):
            script_name = uri.replace("scripts://", "")
            result = mcp.call_resource(f"scripts://{script_name}")
        elif uri == "files://list":
            result = mcp.call_resource("files://list") 
        elif uri.startswith("files://"):
            filename = uri.replace("files://", "")
            result = mcp.call_resource(f"files://{filename}")
        else:
            raise ValidationError(f"Unknown resource URI: {uri}")
        
        return {
            "success": True,
            "uri": uri,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Legacy compatibility endpoints
@app.get("/scripts")
async def list_scripts_compat(user: Optional[str] = Depends(get_current_user)):
    """Legacy compatibility endpoint for listing scripts"""
    try:
        from mcp_server import list_scripts
        result = list_scripts()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files_compat(user: Optional[str] = Depends(get_current_user)):
    """Legacy compatibility endpoint for listing files"""
    try:
        from mcp_server import list_files
        result = list_files()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ElevenLabs integration endpoints
@app.get("/mcp/info")
async def mcp_server_info():
    """MCP server information for ElevenLabs discovery"""
    try:
        return {
            "mcp_version": "2.0.0",
            "server_name": "Reverse Notebook LM",
            "server_version": "2.0.0",
            "server_type": "FastMCP",
            "capabilities": {
                "tools": True,
                "resources": True,
                "scripts": True,
                "files": True,
                "voice_integration": True,
                "type_safety": True,
                "structured_errors": True
            },
            "security": {
                "authentication_enabled": API_KEY is not None,
                "cors_configured": True,
                "allowed_origins": ALLOWED_ORIGINS,
                "dynamic_cors": True,
                "supports_ngrok": True,
                "supports_elevenlabs": True
            },
            "endpoints": {
                "tools": "/tools",
                "resources": "/resources"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HTTP MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--origins", help="Comma-separated list of allowed origins")
    
    args = parser.parse_args()
    
    # Set environment variables from command line
    if args.api_key:
        os.environ["MCP_API_KEY"] = args.api_key
    if args.origins:
        os.environ["ALLOWED_ORIGINS"] = args.origins
    
    print(f"🚀 Starting HTTP MCP Server v2.0.0")
    print(f"📍 Server: {args.host}:{args.port}")
    print(f"🔒 Security: {'Enabled' if API_KEY else 'Disabled'}")
    print(f"🌐 CORS Origins: {ALLOWED_ORIGINS}")
    print(f"📚 Documentation: http://{args.host}:{args.port}/docs")
    print(f"")
    print(f"Available endpoints:")
    print(f"  🏠 GET  / - Server information")
    print(f"  ❤️  GET  /health - Health check")
    print(f"  🔧 GET  /tools - List MCP tools")
    print(f"  ⚡ POST /tools/call - Call MCP tools")
    print(f"  📂 GET  /resources - List MCP resources") 
    print(f"  🎯 POST /resources/get - Get specific resource")
    print(f"  🎬 GET  /scripts - List scripts (legacy)")
    print(f"  📄 GET  /files - List files (legacy)")
    print(f"  ℹ️  GET  /mcp/info - MCP server info")
    
    uvicorn.run(
        "http_mcp_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )