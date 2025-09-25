import json
from pathlib import Path
from typing import Dict, Optional, Any


class ScriptLibrary:
    """Manage and load interactive scripts"""
    
    def __init__(self, scripts_dir: str = "./scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.scripts_dir.mkdir(exist_ok=True)
        self.current_script: Optional[Dict] = None
        self.current_stage: int = 0
        self._initialize_default_scripts()
    
    def _initialize_default_scripts(self):
        """Initialize default scripts if they don't exist"""
        scripts = {
            "blog_writer": {
                "name": "Blog Post Writing Assistant",
                "description": "Helps create engaging blog posts through conversation",
                "stages": [
                    {
                        "name": "discovery",
                        "prompt": "First, let's explore your topic. What are you passionate about? What unique perspective do you bring?",
                        "questions": ["What's your main message?", "Who's your audience?", "What's your unique angle?"]
                    },
                    {
                        "name": "outline",
                        "prompt": "Now let's structure your ideas into a compelling narrative...",
                        "actions": ["create_outline", "suggest_sections"]
                    },
                    {
                        "name": "writing",
                        "prompt": "Let's bring your outline to life with engaging prose...",
                        "actions": ["write_section", "add_examples", "refine_tone"]
                    }
                ],
                "output_format": "markdown",
                "interactive_elements": ["brainstorming", "feedback_loops", "style_coaching"]
            },
            
            "improv_game": {
                "name": "Yes, And... Improv Game",
                "description": "Play collaborative storytelling games",
                "stages": [
                    {
                        "name": "setup",
                        "prompt": "Let's create a story together! I'll start with a scenario, and we'll build on each other's ideas using 'Yes, and...'",
                        "rules": ["Accept what's given", "Add new information", "Keep it flowing"]
                    },
                    {
                        "name": "play",
                        "prompt": "Remember to build on what I say and add your own twist!",
                        "actions": ["continue_story", "add_character", "introduce_conflict"]
                    }
                ],
                "output_format": "markdown",
                "save_transcript": True
            },
            
            "email_workshop": {
                "name": "Email Writing Workshop",
                "description": "Craft effective emails through guided practice",
                "stages": [
                    {
                        "name": "context",
                        "prompt": "Tell me about the email you need to write. What's the situation?",
                        "questions": ["What's your relationship?", "What outcome do you want?", "Any sensitivities?"]
                    },
                    {
                        "name": "drafting",
                        "prompt": "Let's draft this email together, starting with your key message...",
                        "techniques": ["pyramid_principle", "action_oriented", "empathy_mapping"]
                    }
                ],
                "output_format": "markdown"
            },
            
            "brainstorm_session": {
                "name": "Creative Brainstorming Session",
                "description": "Generate and develop ideas interactively",
                "stages": [
                    {
                        "name": "diverge",
                        "prompt": "Let's generate as many ideas as possible. No judgment, just creativity!",
                        "techniques": ["word_association", "reverse_brainstorming", "scamper_method"]
                    },
                    {
                        "name": "converge",
                        "prompt": "Now let's identify the most promising ideas and develop them further...",
                        "actions": ["rank_ideas", "combine_concepts", "detail_development"]
                    }
                ],
                "output_format": "markdown",
                "deliverable": "idea_map"
            },
            
            "interview_prep": {
                "name": "Interview Preparation Coach",
                "description": "Practice interviews with real-time feedback",
                "stages": [
                    {
                        "name": "setup",
                        "prompt": "Let's prepare for your interview. What role and company?",
                        "preparation": ["research_questions", "story_development", "answer_structure"]
                    },
                    {
                        "name": "practice",
                        "prompt": "I'll ask you interview questions and provide feedback on your responses...",
                        "feedback_areas": ["clarity", "specificity", "energy", "structure"]
                    }
                ],
                "output_format": "markdown",
                "creates": "interview_notes"
            }
        }
        
        # Save scripts to individual JSON files
        for script_name, script_data in scripts.items():
            script_file = self.scripts_dir / f"{script_name}.json"
            if not script_file.exists():
                with open(script_file, 'w', encoding='utf-8') as f:
                    json.dump(script_data, f, indent=2)
    
    def list_available_scripts(self) -> Dict[str, str]:
        """List all available scripts with their descriptions"""
        scripts = {}
        for script_file in self.scripts_dir.glob("*.json"):
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    script_data = json.load(f)
                scripts[script_file.stem] = script_data.get("description", "No description")
            except Exception as e:
                print(f"Error loading script {script_file}: {e}")
        return scripts
    
    def load_script(self, script_name: str) -> Dict[str, Any]:
        """Load a specific script by name"""
        try:
            script_file = self.scripts_dir / f"{script_name}.json"
            if not script_file.exists():
                raise FileNotFoundError(f"Script '{script_name}' not found")
            
            with open(script_file, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            
            self.current_script = script_data
            self.current_stage = 0
            
            return {
                "success": True,
                "script_name": script_name,
                "script_data": script_data,
                "current_stage": self.get_current_stage(),
                "instructions": self.get_stage_instructions()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load script '{script_name}'"
            }
    
    def get_current_stage(self) -> Optional[Dict]:
        """Get the current stage of the active script"""
        if not self.current_script or self.current_stage >= len(self.current_script.get("stages", [])):
            return None
        return self.current_script["stages"][self.current_stage]
    
    def get_stage_instructions(self) -> str:
        """Get instructions for the current stage"""
        stage = self.get_current_stage()
        if not stage:
            return "No active script or stage"
        return stage.get("prompt", "No instructions for this stage")
    
    def advance_stage(self) -> Dict[str, Any]:
        """Move to the next stage of the current script"""
        if not self.current_script:
            return {"success": False, "message": "No active script"}
        
        stages = self.current_script.get("stages", [])
        if self.current_stage >= len(stages) - 1:
            return {
                "success": False,
                "message": "Already at the final stage",
                "is_complete": True
            }
        
        self.current_stage += 1
        return {
            "success": True,
            "current_stage": self.get_current_stage(),
            "instructions": self.get_stage_instructions(),
            "stage_number": self.current_stage + 1,
            "total_stages": len(stages)
        }
    
    def get_script_progress(self) -> Dict[str, Any]:
        """Get progress information about the current script"""
        if not self.current_script:
            return {"active": False}
        
        stages = self.current_script.get("stages", [])
        return {
            "active": True,
            "script_name": self.current_script.get("name"),
            "current_stage": self.current_stage + 1,
            "total_stages": len(stages),
            "stage_name": stages[self.current_stage].get("name") if self.current_stage < len(stages) else None,
            "is_complete": self.current_stage >= len(stages)
        }
    
    def reset_script(self) -> bool:
        """Reset the current script to the beginning"""
        if self.current_script:
            self.current_stage = 0
            return True
        return False
    
    def clear_script(self) -> bool:
        """Clear the current active script"""
        self.current_script = None
        self.current_stage = 0
        return True