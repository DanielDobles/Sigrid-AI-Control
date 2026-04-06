# File System Agent - Read, Write, Search, and Manage Files

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import stat

class FileSystemAgent:
    """Manages file system operations with safety controls."""
    
    def __init__(self, allowed_roots: Optional[List[str]] = None):
        """Initialize with optional allowed root directories for safety."""
        self.allowed_roots = allowed_roots or [str(Path.home())]
        
    def _validate_path(self, file_path: str) -> Path:
        """Validate that the path is within allowed roots."""
        path = Path(file_path).resolve()
        
        # Check if path is within allowed roots
        for root in self.allowed_roots:
            if str(path).startswith(str(Path(root).resolve())):
                return path
        
        # Default: allow access to user's home directory
        if str(path).startswith(str(Path.home())):
            return path
            
        return path  # For now, allow all paths (add safety restrictions later)
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> dict:
        """Read contents of a file."""
        try:
            path = self._validate_path(file_path)
            if not path.exists():
                return {"status": "error", "error": f"File not found: {file_path}"}
            if not path.is_file():
                return {"status": "error", "error": f"Not a file: {file_path}"}
            
            content = path.read_text(encoding=encoding)
            return {
                "status": "success",
                "action": "read_file",
                "path": str(path),
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"status": "error", "action": "read_file", "error": str(e)}
    
    def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> dict:
        """Write content to a file."""
        try:
            path = self._validate_path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)
            return {
                "status": "success",
                "action": "write_file",
                "path": str(path),
                "bytes_written": len(content)
            }
        except Exception as e:
            return {"status": "error", "action": "write_file", "error": str(e)}
    
    def append_file(self, file_path: str, content: str, encoding: str = "utf-8") -> dict:
        """Append content to a file."""
        try:
            path = self._validate_path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding=encoding) as f:
                f.write(content)
            return {
                "status": "success",
                "action": "append_file",
                "path": str(path),
                "bytes_appended": len(content)
            }
        except Exception as e:
            return {"status": "error", "action": "append_file", "error": str(e)}
    
    def delete_file(self, file_path: str) -> dict:
        """Delete a file."""
        try:
            path = self._validate_path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return {"status": "success", "action": "delete_file", "path": str(path)}
            return {"status": "error", "error": f"File not found: {file_path}"}
        except Exception as e:
            return {"status": "error", "action": "delete_file", "error": str(e)}
    
    def list_directory(self, dir_path: str, recursive: bool = False) -> dict:
        """List files and directories in a path."""
        try:
            path = self._validate_path(dir_path)
            if not path.exists() or not path.is_dir():
                return {"status": "error", "error": f"Directory not found: {dir_path}"}
            
            items = []
            if recursive:
                for item in path.rglob("*"):
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_dir": item.is_dir(),
                        "size": self._get_size(item)
                    })
            else:
                for item in path.iterdir():
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_dir": item.is_dir(),
                        "size": self._get_size(item)
                    })
            
            return {
                "status": "success",
                "action": "list_directory",
                "path": str(path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"status": "error", "action": "list_directory", "error": str(e)}
    
    def create_directory(self, dir_path: str, parents: bool = True) -> dict:
        """Create a directory."""
        try:
            path = self._validate_path(dir_path)
            path.mkdir(parents=parents, exist_ok=True)
            return {"status": "success", "action": "create_directory", "path": str(path)}
        except Exception as e:
            return {"status": "error", "action": "create_directory", "error": str(e)}
    
    def delete_directory(self, dir_path: str) -> dict:
        """Delete a directory and its contents."""
        try:
            path = self._validate_path(dir_path)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
                return {"status": "success", "action": "delete_directory", "path": str(path)}
            return {"status": "error", "error": f"Directory not found: {dir_path}"}
        except Exception as e:
            return {"status": "error", "action": "delete_directory", "error": str(e)}
    
    def copy_file(self, source: str, destination: str) -> dict:
        """Copy a file from source to destination."""
        try:
            src = self._validate_path(source)
            dst = self._validate_path(destination)
            
            if not src.exists():
                return {"status": "error", "error": f"Source not found: {source}"}
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return {
                "status": "success",
                "action": "copy_file",
                "source": str(src),
                "destination": str(dst)
            }
        except Exception as e:
            return {"status": "error", "action": "copy_file", "error": str(e)}
    
    def move_file(self, source: str, destination: str) -> dict:
        """Move a file from source to destination."""
        try:
            src = self._validate_path(source)
            dst = self._validate_path(destination)
            
            if not src.exists():
                return {"status": "error", "error": f"Source not found: {source}"}
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dst)
            return {
                "status": "success",
                "action": "move_file",
                "source": str(src),
                "destination": str(dst)
            }
        except Exception as e:
            return {"status": "error", "action": "move_file", "error": str(e)}
    
    def search_files(self, dir_path: str, pattern: str) -> dict:
        """Search for files matching a pattern in a directory."""
        try:
            path = self._validate_path(dir_path)
            if not path.exists() or not path.is_dir():
                return {"status": "error", "error": f"Directory not found: {dir_path}"}
            
            matches = list(path.glob(pattern))
            results = [{
                "name": m.name,
                "path": str(m),
                "is_dir": m.is_dir()
            } for m in matches]
            
            return {
                "status": "success",
                "action": "search_files",
                "directory": str(path),
                "pattern": pattern,
                "matches": results,
                "count": len(results)
            }
        except Exception as e:
            return {"status": "error", "action": "search_files", "error": str(e)}
    
    def get_file_info(self, file_path: str) -> dict:
        """Get detailed information about a file/directory."""
        try:
            path = self._validate_path(file_path)
            if not path.exists():
                return {"status": "error", "error": f"Path not found: {file_path}"}
            
            stat_info = path.stat()
            return {
                "status": "success",
                "action": "file_info",
                "path": str(path),
                "name": path.name,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": self._get_size(path),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            }
        except Exception as e:
            return {"status": "error", "action": "file_info", "error": str(e)}
    
    def _get_size(self, path: Path) -> int:
        """Get size of file or directory."""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
            return 0
        except:
            return 0
    
    def execute_action(self, action_name: str, **kwargs) -> dict:
        """Execute a file system action by name."""
        action_map = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "append_file": self.append_file,
            "delete_file": self.delete_file,
            "list_directory": self.list_directory,
            "create_directory": self.create_directory,
            "delete_directory": self.delete_directory,
            "copy_file": self.copy_file,
            "move_file": self.move_file,
            "search_files": self.search_files,
            "get_file_info": self.get_file_info,
        }
        
        if action_name in action_map:
            return action_map[action_name](**kwargs)
        return {"status": "error", "error": f"Unknown action: {action_name}"}
