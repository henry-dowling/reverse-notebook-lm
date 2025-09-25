from typing import Dict, Any, Optional
from handlers.file_handler import FileHandler
import json


class FileOperationTool:
    """Tool for performing operations on local markdown files"""
    
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler
        self.name = "file_operation"
    
    async def execute(
        self, 
        operation: str,
        filename: str = "output.md",
        content: Optional[str] = None,
        line_number: Optional[int] = None,
        pattern: Optional[str] = None,
        replacement: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a file operation
        
        Args:
            operation: Type of operation to perform
            filename: Target markdown file
            content: Content for write operations
            line_number: Line number for insert operations
            pattern: Search pattern for replace operations
            replacement: Replacement text for replace operations
            
        Returns:
            Dictionary with operation results
        """
        try:
            if operation == "create":
                filepath = self.file_handler.create_file(filename, content or "")
                return {
                    "success": True,
                    "operation": "create",
                    "filepath": filepath,
                    "message": f"Created file: {filename}"
                }
            
            elif operation == "read":
                content = self.file_handler.read_file(filename)
                return {
                    "success": True,
                    "operation": "read",
                    "filepath": str(self.file_handler.working_dir / filename),
                    "content": content,
                    "message": f"Read file: {filename}"
                }
            
            elif operation == "write":
                if content is None:
                    raise ValueError("Content is required for write operation")
                
                self.file_handler.write_file(filename, content)
                return {
                    "success": True,
                    "operation": "write",
                    "filepath": str(self.file_handler.working_dir / filename),
                    "message": f"Wrote to file: {filename}"
                }
            
            elif operation == "append":
                if content is None:
                    raise ValueError("Content is required for append operation")
                
                self.file_handler.append_to_file(filename, content)
                return {
                    "success": True,
                    "operation": "append",
                    "filepath": str(self.file_handler.working_dir / filename),
                    "message": f"Appended to file: {filename}"
                }
            
            elif operation == "insert":
                if content is None or line_number is None:
                    raise ValueError("Content and line_number are required for insert operation")
                
                self.file_handler.insert_at_line(filename, line_number, content)
                return {
                    "success": True,
                    "operation": "insert",
                    "filepath": str(self.file_handler.working_dir / filename),
                    "line_number": line_number,
                    "message": f"Inserted content at line {line_number} in {filename}"
                }
            
            elif operation == "replace":
                if pattern is None or replacement is None:
                    raise ValueError("Pattern and replacement are required for replace operation")
                
                count = self.file_handler.find_and_replace(filename, pattern, replacement)
                return {
                    "success": True,
                    "operation": "replace",
                    "filepath": str(self.file_handler.working_dir / filename),
                    "replacements": count,
                    "message": f"Made {count} replacements in {filename}"
                }
            
            elif operation == "save_as":
                if content is None:
                    raise ValueError("Content is required for save_as operation")
                
                # Read current file and save with new name
                original_content = self.file_handler.read_file(self.file_handler.current_file or "output.md")
                new_filepath = self.file_handler.create_file(filename, content or original_content)
                return {
                    "success": True,
                    "operation": "save_as",
                    "filepath": new_filepath,
                    "message": f"Saved as: {filename}"
                }
            
            elif operation == "list":
                files = self.file_handler.list_files()
                return {
                    "success": True,
                    "operation": "list",
                    "files": files,
                    "message": f"Found {len(files)} markdown files"
                }
            
            elif operation == "backup":
                backup_path = self.file_handler.create_backup(filename)
                return {
                    "success": True,
                    "operation": "backup",
                    "backup_path": backup_path,
                    "message": f"Created backup of {filename}"
                }
            
            elif operation == "info":
                info = self.file_handler.get_file_info(filename)
                return {
                    "success": True,
                    "operation": "info",
                    "file_info": info,
                    "message": f"File info for {filename}"
                }
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "error": str(e),
                "message": f"Failed to {operation} file: {str(e)}"
            }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for OpenAI function calling"""
        return {
            "type": "function",
            "name": self.name,
            "description": "Perform operations on local markdown files",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["create", "read", "write", "append", "insert", "replace", "save_as", "list", "backup", "info"],
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
                        "description": "Line number for insert operations (1-indexed)"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Regular expression pattern to search for in replace operations"
                    },
                    "replacement": {
                        "type": "string",
                        "description": "Replacement text for replace operations"
                    }
                },
                "required": ["operation"]
            }
        }