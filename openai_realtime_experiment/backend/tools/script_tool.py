from typing import Dict, Any
from handlers.script_library import ScriptLibrary


class ScriptLoaderTool:
    """Tool for loading and managing interactive scripts"""
    
    def __init__(self, script_library: ScriptLibrary):
        self.script_library = script_library
        self.name = "load_script"
    
    async def execute(self, script_name: str) -> Dict[str, Any]:
        """
        Load and activate an interactive script
        
        Args:
            script_name: Name of the script to load
            
        Returns:
            Dictionary with script loading results
        """
        try:
            # Load the script
            result = self.script_library.load_script(script_name)
            
            if result["success"]:
                # Get current stage information
                current_stage = self.script_library.get_current_stage()
                instructions = self.script_library.get_stage_instructions()
                progress = self.script_library.get_script_progress()
                
                return {
                    "success": True,
                    "script_name": script_name,
                    "script_title": result["script_data"]["name"],
                    "script_description": result["script_data"]["description"],
                    "current_stage": current_stage["name"] if current_stage else None,
                    "instructions": instructions,
                    "progress": progress,
                    "message": f"Loaded script: {result['script_data']['name']}"
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load script '{script_name}': {str(e)}"
            }
    
    async def list_scripts(self) -> Dict[str, Any]:
        """List all available scripts"""
        try:
            scripts = self.script_library.list_available_scripts()
            return {
                "success": True,
                "scripts": scripts,
                "message": f"Found {len(scripts)} available scripts"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list scripts: {str(e)}"
            }
    
    async def get_progress(self) -> Dict[str, Any]:
        """Get current script progress"""
        try:
            progress = self.script_library.get_script_progress()
            return {
                "success": True,
                "progress": progress,
                "message": "Retrieved script progress"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get progress: {str(e)}"
            }
    
    async def advance_stage(self) -> Dict[str, Any]:
        """Advance to the next stage of the current script"""
        try:
            result = self.script_library.advance_stage()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to advance stage: {str(e)}"
            }
    
    async def reset_script(self) -> Dict[str, Any]:
        """Reset the current script to the beginning"""
        try:
            success = self.script_library.reset_script()
            if success:
                progress = self.script_library.get_script_progress()
                instructions = self.script_library.get_stage_instructions()
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
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to reset script: {str(e)}"
            }
    
    async def clear_script(self) -> Dict[str, Any]:
        """Clear the current active script"""
        try:
            success = self.script_library.clear_script()
            return {
                "success": success,
                "message": "Cleared active script" if success else "No active script to clear"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to clear script: {str(e)}"
            }
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """Get the tool definition for OpenAI function calling"""
        return {
            "type": "function",
            "name": self.name,
            "description": "Load an interactive script to guide the conversation",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_name": {
                        "type": "string",
                        "description": "Name of the script to load (e.g., 'blog_writer', 'improv_game', 'email_workshop', 'brainstorm_session', 'interview_prep')",
                        "enum": ["blog_writer", "improv_game", "email_workshop", "brainstorm_session", "interview_prep"]
                    }
                },
                "required": ["script_name"]
            }
        }