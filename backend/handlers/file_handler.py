import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import re


class FileHandler:
    """Handle local markdown file operations"""
    
    def __init__(self, working_dir: str = "./workspace"):
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(exist_ok=True)
        self.current_file: Optional[str] = None
    
    def create_file(self, filename: str, content: str = "") -> str:
        """Create new markdown file with initial content"""
        try:
            filepath = self.working_dir / filename
            if not filename.endswith('.md'):
                filename += '.md'
                filepath = self.working_dir / filename
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = filename
            return str(filepath)
        except Exception as e:
            raise Exception(f"Failed to create file {filename}: {str(e)}")
    
    def read_file(self, filename: str) -> str:
        """Read markdown file content"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
            
            filepath = self.working_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"File {filename} does not exist")
                
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read file {filename}: {str(e)}")
    
    def write_file(self, filename: str, content: str) -> bool:
        """Write content to markdown file (overwrites existing content)"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
                
            filepath = self.working_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = filename
            return True
        except Exception as e:
            raise Exception(f"Failed to write file {filename}: {str(e)}")
    
    def append_to_file(self, filename: str, content: str) -> bool:
        """Append content to existing file"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
                
            filepath = self.working_dir / filename
            
            # Create file if it doesn't exist
            if not filepath.exists():
                self.create_file(filename, content)
                return True
            
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to append to file {filename}: {str(e)}")
    
    def insert_at_line(self, filename: str, line_num: int, content: str) -> bool:
        """Insert content at specific line number"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
                
            filepath = self.working_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"File {filename} does not exist")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Insert at specified line (1-indexed)
            if line_num < 1:
                line_num = 1
            elif line_num > len(lines) + 1:
                line_num = len(lines) + 1
            
            lines.insert(line_num - 1, content + '\n' if not content.endswith('\n') else content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to insert into file {filename} at line {line_num}: {str(e)}")
    
    def find_and_replace(self, filename: str, pattern: str, replacement: str) -> int:
        """Replace all occurrences of pattern and return count of replacements"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
                
            filepath = self.working_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"File {filename} does not exist")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count and perform replacements
            new_content = re.sub(pattern, replacement, content)
            replacement_count = len(re.findall(pattern, content))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return replacement_count
        except Exception as e:
            raise Exception(f"Failed to replace in file {filename}: {str(e)}")
    
    def create_backup(self, filename: str) -> str:
        """Create timestamped backup of file"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
                
            filepath = self.working_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"File {filename} does not exist")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{filepath.stem}_backup_{timestamp}.md"
            backup_path = self.working_dir / backup_name
            
            with open(filepath, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            return str(backup_path)
        except Exception as e:
            raise Exception(f"Failed to create backup of {filename}: {str(e)}")
    
    def list_files(self) -> list:
        """List all markdown files in working directory"""
        try:
            return [f.name for f in self.working_dir.iterdir() if f.suffix == '.md']
        except Exception as e:
            raise Exception(f"Failed to list files: {str(e)}")
    
    def get_file_info(self, filename: str) -> dict:
        """Get file information including size and modification time"""
        try:
            if not filename.endswith('.md'):
                filename += '.md'
                
            filepath = self.working_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"File {filename} does not exist")
            
            stat = filepath.stat()
            return {
                "name": filename,
                "path": str(filepath),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to get file info for {filename}: {str(e)}")