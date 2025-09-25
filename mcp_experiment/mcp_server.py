#!/usr/bin/env python3
"""
MCP Server for Reverse Notebook LM using FastMCP
Provides tools for retrieving scripts and editing files with proper type safety
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re

# Import FastMCP components
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import our existing handlers
from handlers.script_library import ScriptLibrary
from handlers.file_handler import FileHandler
from config import WORKING_DIRECTORY

# Initialize FastMCP server
mcp = FastMCP("Reverse Notebook LM")

# Initialize handlers
script_library = ScriptLibrary()
file_handler = FileHandler(WORKING_DIRECTORY)

# Custom exception classes for better error handling
class MCPError(Exception):
    """Base exception for MCP operations"""
    pass

class ScriptNotFoundError(MCPError):
    """Raised when a requested script is not found"""
    pass

class FileOperationError(MCPError):
    """Raised when file operations fail"""
    pass

class ValidationError(MCPError):
    """Raised when input validation fails"""
    pass

# Pydantic models for structured data
class ScriptInfo(BaseModel):
    """Information about an interactive script"""
    name: str = Field(description="Script name")
    description: str = Field(description="Script description")
    stages: int = Field(description="Number of stages in the script")
    category: str = Field(description="Script category")

class ScriptProgress(BaseModel):
    """Current progress in a loaded script"""
    active_script: Optional[str] = Field(description="Name of currently active script")
    current_stage: int = Field(description="Current stage number (0-indexed)")
    total_stages: int = Field(description="Total number of stages")
    stage_title: str = Field(description="Title of current stage")
    completed: bool = Field(description="Whether script is completed")

class FileInfo(BaseModel):
    """Information about a file"""
    filename: str = Field(description="Name of the file")
    size: int = Field(description="File size in bytes")
    modified: str = Field(description="Last modified timestamp")
    exists: bool = Field(description="Whether file exists")

class LineEdit(BaseModel):
    """Single line edit operation"""
    line_number: int = Field(ge=1, description="Line number to edit (1-indexed)")
    new_content: str = Field(description="New content for the line")

# Resources - read-only data access
@mcp.resource("scripts://list")
def get_scripts_resource() -> Dict[str, str]:
    """Resource providing list of available scripts"""
    return script_library.list_available_scripts()

@mcp.resource("scripts://{script_name}")
def get_script_resource(script_name: str) -> Dict[str, Any]:
    """Resource providing detailed script information"""
    script_file = Path(script_library.scripts_dir) / f"{script_name}.json"
    if not script_file.exists():
        raise ScriptNotFoundError(f"Script '{script_name}' not found")
    
    with open(script_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@mcp.resource("files://list")
def get_files_resource() -> List[str]:
    """Resource providing list of available files"""
    return file_handler.list_files()

@mcp.resource("files://{filename}")
def get_file_resource(filename: str) -> str:
    """Resource providing file content"""
    try:
        return file_handler.read_file(filename)
    except Exception as e:
        raise FileOperationError(f"Failed to read file '{filename}': {str(e)}")

# Tools - interactive operations with side effects
@mcp.tool()
def list_scripts() -> Dict[str, Any]:
    """
    List all available interactive scripts with their descriptions.
    
    Returns:
        Dictionary containing success status, scripts list, and count
    """
    try:
        scripts = script_library.list_available_scripts()
        return {
            "success": True,
            "scripts": scripts,
            "count": len(scripts),
            "message": f"Found {len(scripts)} available scripts"
        }
    except Exception as e:
        raise MCPError(f"Failed to list scripts: {str(e)}")

@mcp.tool()
def get_script(script_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific script.
    
    Args:
        script_name: Name of the script to retrieve (e.g., 'blog_writer', 'improv_game')
        
    Returns:
        Dictionary with script details and metadata
    """
    if not script_name:
        raise ValidationError("script_name is required")
    
    try:
        script_file = Path(script_library.scripts_dir) / f"{script_name}.json"
        if not script_file.exists():
            raise ScriptNotFoundError(f"Script '{script_name}' not found")
        
        with open(script_file, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        
        return {
            "success": True,
            "script_name": script_name,
            "script_data": script_data
        }
    except ScriptNotFoundError:
        raise
    except Exception as e:
        raise MCPError(f"Failed to get script '{script_name}': {str(e)}")

@mcp.tool()
def load_script(script_name: str) -> Dict[str, Any]:
    """
    Load and activate an interactive script for execution.
    
    Args:
        script_name: Name of the script to load and activate
        
    Returns:
        Dictionary with load status and initial instructions
    """
    if not script_name:
        raise ValidationError("script_name is required")
    
    try:
        result = script_library.load_script(script_name)
        return result
    except Exception as e:
        raise MCPError(f"Failed to load script '{script_name}': {str(e)}")

@mcp.tool()
def get_script_progress() -> ScriptProgress:
    """
    Get current progress and stage information for the active script.
    
    Returns:
        ScriptProgress model with current state information
    """
    try:
        progress = script_library.get_script_progress()
        return ScriptProgress(**progress)
    except Exception as e:
        raise MCPError(f"Failed to get script progress: {str(e)}")

@mcp.tool()
def advance_script_stage() -> Dict[str, Any]:
    """
    Advance to the next stage of the currently active script.
    
    Returns:
        Dictionary with advancement status and new stage information
    """
    try:
        result = script_library.advance_stage()
        return result
    except Exception as e:
        raise MCPError(f"Failed to advance script stage: {str(e)}")

@mcp.tool()
def reset_script() -> Dict[str, Any]:
    """
    Reset the currently active script back to the beginning.
    
    Returns:
        Dictionary with reset status and initial stage information
    """
    try:
        success = script_library.reset_script()
        if success:
            progress = script_library.get_script_progress()
            instructions = script_library.get_stage_instructions()
            return {
                "success": True,
                "progress": progress,
                "instructions": instructions,
                "message": "Script reset to beginning"
            }
        else:
            return {
                "success": False,
                "message": "No active script to reset"
            }
    except Exception as e:
        raise MCPError(f"Failed to reset script: {str(e)}")

@mcp.tool()
def clear_script() -> Dict[str, Any]:
    """
    Clear the currently active script and return to idle state.
    
    Returns:
        Dictionary with clear operation status
    """
    try:
        success = script_library.clear_script()
        return {
            "success": success,
            "message": "Cleared active script" if success else "No active script to clear"
        }
    except Exception as e:
        raise MCPError(f"Failed to clear script: {str(e)}")

@mcp.tool()
def read_file(filename: str = "output.md") -> Dict[str, Any]:
    """
    Read the contents of a markdown file from the workspace.
    
    Args:
        filename: Name of the markdown file to read (defaults to 'output.md')
        
    Returns:
        Dictionary with file contents and metadata
    """
    try:
        content = file_handler.read_file(filename)
        return {
            "success": True,
            "filename": filename,
            "content": content,
            "message": f"Read file: {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to read file '{filename}': {str(e)}")

@mcp.tool()
def write_file(content: str, filename: str = "output.md") -> Dict[str, Any]:
    """
    Write content to a markdown file, overwriting existing content.
    
    Args:
        content: Content to write to the file
        filename: Name of the markdown file to write to (defaults to 'output.md')
        
    Returns:
        Dictionary with write operation status
    """
    if not content:
        raise ValidationError("content is required")
    
    try:
        file_handler.write_file(filename, content)
        return {
            "success": True,
            "filename": filename,
            "message": f"Wrote to file: {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to write file '{filename}': {str(e)}")

@mcp.tool()
def append_file(content: str, filename: str = "output.md") -> Dict[str, Any]:
    """
    Append content to an existing markdown file.
    
    Args:
        content: Content to append to the file
        filename: Name of the markdown file to append to (defaults to 'output.md')
        
    Returns:
        Dictionary with append operation status
    """
    if not content:
        raise ValidationError("content is required")
    
    try:
        file_handler.append_to_file(filename, content)
        return {
            "success": True,
            "filename": filename,
            "message": f"Appended to file: {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to append to file '{filename}': {str(e)}")

@mcp.tool()
def insert_file_content(line_number: int, content: str, filename: str = "output.md") -> Dict[str, Any]:
    """
    Insert content at a specific line number in a markdown file.
    
    Args:
        line_number: Line number to insert content at (1-indexed)
        content: Content to insert
        filename: Name of the markdown file to modify (defaults to 'output.md')
        
    Returns:
        Dictionary with insert operation status
    """
    if line_number < 1:
        raise ValidationError("line_number must be >= 1")
    if not content:
        raise ValidationError("content is required")
    
    try:
        file_handler.insert_at_line(filename, line_number, content)
        return {
            "success": True,
            "filename": filename,
            "line_number": line_number,
            "message": f"Inserted content at line {line_number} in {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to insert content in '{filename}': {str(e)}")

@mcp.tool()
def replace_file_content(pattern: str, replacement: str, filename: str = "output.md") -> Dict[str, Any]:
    """
    Replace all occurrences of a regular expression pattern in a markdown file.
    
    Args:
        pattern: Regular expression pattern to search for
        replacement: Replacement text
        filename: Name of the markdown file to modify (defaults to 'output.md')
        
    Returns:
        Dictionary with replacement operation status and count
    """
    if not pattern:
        raise ValidationError("pattern is required")
    if replacement is None:
        raise ValidationError("replacement is required")
    
    try:
        # Validate regex pattern
        re.compile(pattern)
        
        count = file_handler.find_and_replace(filename, pattern, replacement)
        return {
            "success": True,
            "filename": filename,
            "replacements": count,
            "message": f"Made {count} replacements in {filename}"
        }
    except re.error as e:
        raise ValidationError(f"Invalid regex pattern: {str(e)}")
    except Exception as e:
        raise FileOperationError(f"Failed to replace content in '{filename}': {str(e)}")

@mcp.tool()
def list_files() -> Dict[str, Any]:
    """
    List all markdown files in the workspace directory.
    
    Returns:
        Dictionary with list of files and count
    """
    try:
        files = file_handler.list_files()
        return {
            "success": True,
            "files": files,
            "count": len(files),
            "message": f"Found {len(files)} markdown files"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to list files: {str(e)}")

@mcp.tool()
def get_file_info(filename: str) -> FileInfo:
    """
    Get detailed information about a specific file.
    
    Args:
        filename: Name of the file to get information for
        
    Returns:
        FileInfo model with file metadata
    """
    if not filename:
        raise ValidationError("filename is required")
    
    try:
        info = file_handler.get_file_info(filename)
        return FileInfo(**info)
    except Exception as e:
        raise FileOperationError(f"Failed to get file info for '{filename}': {str(e)}")

@mcp.tool()
def create_file(filename: str, content: str = "") -> Dict[str, Any]:
    """
    Create a new markdown file with optional initial content.
    
    Args:
        filename: Name of the file to create
        content: Initial content for the file (defaults to empty)
        
    Returns:
        Dictionary with creation status and file path
    """
    if not filename:
        raise ValidationError("filename is required")
    
    try:
        filepath = file_handler.create_file(filename, content)
        return {
            "success": True,
            "filename": filename,
            "filepath": str(filepath),
            "message": f"Created file: {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to create file '{filename}': {str(e)}")

@mcp.tool()
def edit_file_lines(line_edits: List[LineEdit], filename: str = "output.md") -> Dict[str, Any]:
    """
    Edit specific lines of a markdown file by replacing content at specified line numbers.
    
    Args:
        line_edits: List of LineEdit objects with line_number and new_content
        filename: Name of the markdown file to edit (defaults to 'output.md')
        
    Returns:
        Dictionary with edit operation status and summary
    """
    if not line_edits:
        raise ValidationError("line_edits is required")
    
    try:
        # Read the current file content
        try:
            current_content = file_handler.read_file(filename)
            lines = current_content.split('\n')
        except FileNotFoundError:
            # Create file if it doesn't exist
            lines = []
        
        # Sort edits by line number (descending) to avoid index shifting issues
        sorted_edits = sorted(line_edits, key=lambda x: x.line_number, reverse=True)
        edited_lines = []
        
        for edit in sorted_edits:
            line_number = edit.line_number
            new_content = edit.new_content
            
            # If line number is beyond current file length, extend with empty lines
            while len(lines) < line_number:
                lines.append("")
            
            # Edit the specific line (convert to 0-indexed)
            lines[line_number - 1] = new_content
            edited_lines.append(line_number)
        
        # Write the modified content back to the file
        new_content = '\n'.join(lines)
        file_handler.write_file(filename, new_content)
        
        return {
            "success": True,
            "filename": filename,
            "edited_lines": edited_lines,
            "total_lines": len(lines),
            "message": f"Edited {len(edited_lines)} lines in {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to edit lines in '{filename}': {str(e)}")

@mcp.tool()
def create_backup(filename: str) -> Dict[str, Any]:
    """
    Create a timestamped backup of a file.
    
    Args:
        filename: Name of the file to backup
        
    Returns:
        Dictionary with backup operation status and backup path
    """
    if not filename:
        raise ValidationError("filename is required")
    
    try:
        backup_path = file_handler.create_backup(filename)
        return {
            "success": True,
            "filename": filename,
            "backup_path": str(backup_path),
            "message": f"Created backup of {filename}"
        }
    except Exception as e:
        raise FileOperationError(f"Failed to create backup of '{filename}': {str(e)}")

# Context injection for logging (if needed)
def setup_logging_context():
    """Setup logging context for the MCP server"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("reverse-notebook-lm-mcp")

if __name__ == "__main__":
    # Setup logging
    logger = setup_logging_context()
    logger.info("Starting Reverse Notebook LM MCP Server")
    
    # Run the FastMCP server
    mcp.run()