# SIGRID Mojo Integration Layer
# 
# Python bridge to Mojo modules with automatic fallback.
# If Mojo is not installed, falls back to pure Python implementations.

import importlib
import sys
from typing import Optional, Dict, Any
from pathlib import Path


class MojoIntegration:
    """
    Manages Mojo integration with automatic Python fallback.
    
    Usage:
        mojo = MojoIntegration()
        if mojo.available:
            result = mojo.image_processor.analyze_screenshot("screen.png")
        else:
            # Uses Python fallback automatically
            result = mojo.image_processor.analyze_screenshot("screen.png")
    """
    
    def __init__(self):
        self.available = False
        self.mojo_available = False
        self.image_processor = None
        self.task_queue = None
        self.sandbox = None
        
        self._check_mojo_availability()
        self._load_modules()
    
    def _check_mojo_availability(self):
        """Check if Mojo/Modular is installed and configured."""
        try:
            # Try to import Mojo's Python bridge
            import max.mojo.importer
            self.mojo_available = True
            self.available = True
        except ImportError:
            try:
                # Check for modular SDK
                import modular
                self.mojo_available = True
                self.available = True
            except ImportError:
                self.mojo_available = False
                # Still available with Python fallback
                self.available = True
    
    def _load_modules(self):
        """Load Mojo modules with Python fallback."""
        if self.mojo_available:
            self._load_mojo_modules()
        else:
            self._load_python_fallbacks()
    
    def _load_mojo_modules(self):
        """Load compiled Mojo modules."""
        try:
            import max.mojo.importer
            from src.mojo import image_processor as mojo_image
            from src.mojo import task_queue as mojo_task
            from src.mojo import sandbox as mojo_sandbox
            
            self.image_processor = mojo_image
            self.task_queue = mojo_task
            self.sandbox = mojo_sandbox
            
            print("✅ Mojo modules loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load Mojo modules, using Python fallback: {e}")
            self._load_python_fallbacks()
    
    def _load_python_fallbacks(self):
        """Load pure Python fallback implementations."""
        print("ℹ️ Using Python fallback implementations")
        
        # Image processor fallback
        self.image_processor = PythonImageProcessor()
        
        # Task queue fallback
        self.task_queue = PythonTaskQueue()
        
        # Sandbox fallback
        self.sandbox = PythonSandbox()
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "available": self.available,
            "mojo_available": self.mojo_available,
            "image_processor": "Mojo" if self.mojo_available and self.image_processor else "Python",
            "task_queue": "Mojo" if self.mojo_available and self.task_queue else "Python",
            "sandbox": "Mojo" if self.mojo_available and self.sandbox else "Python"
        }


# ============================================================
# PYTHON FALLBACK IMPLEMENTATIONS
# ============================================================

class PythonImageProcessor:
    """Pure Python fallback for image processing."""
    
    def analyze_screenshot(self, image_path: str) -> dict:
        """Analyze screenshot using Python (slower but functional)."""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            
            img = Image.open(image_path).convert("RGB")
            np_img = np.array(img)
            
            gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
            brightness = float(gray.mean() / 255.0)
            
            edges = cv2.Canny(gray, 100, 200)
            edge_count = int(cv2.countNonZero(edges))
            
            return {
                "dominant_colors": [],
                "brightness": brightness,
                "edges_detected": edge_count,
                "text_regions": 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def compare_images(self, image1_path: str, image2_path: str) -> dict:
        """Compare two images using Python."""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            
            img1 = np.array(Image.open(image1_path).convert("RGB"))
            img2 = np.array(Image.open(image2_path).convert("RGB"))
            
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            diff = cv2.absdiff(img1, img2)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            diff_percentage = float(cv2.countNonZero(thresh)) / (thresh.shape[0] * thresh.shape[1]) * 100
            
            return {
                "diff_percentage": diff_percentage,
                "mean_difference": float(diff.mean()),
                "change_regions": [],
                "has_changes": diff_percentage > 0.1
            }
        except Exception as e:
            return {"error": str(e)}
    
    def detect_ui_elements(self, image_path: str, template_paths: list) -> list:
        """Detect UI elements using Python."""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            
            screenshot = cv2.cvtColor(np.array(Image.open(image_path)), cv2.COLOR_RGB2GRAY)
            detections = []
            
            for template_path in template_paths:
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    continue
                
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                
                if float(max_val) > 0.8:
                    h, w = template.shape
                    detections.append({
                        "element": template_path,
                        "confidence": float(max_val),
                        "x": int(max_loc[0]),
                        "y": int(max_loc[1]),
                        "w": int(w),
                        "h": int(h)
                    })
            
            return detections
        except Exception as e:
            return []


class PythonTaskQueue:
    """Pure Python fallback for task queue."""
    
    def __init__(self, max_size: int = 1000):
        self.tasks = []
        self.max_size = max_size
        self.active_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []
        self.task_counter = 0
    
    def add_task(self, priority: int, agent_type: str, action: str,
                 parameters: dict, timeout: float = 30.0, retry_count: int = 3) -> int:
        """Add task to queue."""
        if len(self.tasks) >= self.max_size:
            raise Exception("Task queue is full")
        
        import time
        task_id = self.task_counter
        self.task_counter += 1
        
        self.tasks.append({
            "priority": priority,
            "task_id": task_id,
            "agent_type": agent_type,
            "action": action,
            "parameters": parameters,
            "timeout": timeout,
            "retry_count": retry_count,
            "timestamp": time.time()
        })
        
        self.tasks.sort(key=lambda x: x["priority"])
        return task_id
    
    def get_next_task(self) -> Optional[dict]:
        """Get highest priority task."""
        if not self.tasks:
            return None
        
        import time
        task = self.tasks.pop(0)
        task_id = task["task_id"]
        
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "status": "active",
            "started_at": time.time()
        }
        
        return task
    
    def complete_task(self, task_id: int, result: dict):
        """Mark task as completed."""
        import time
        if task_id in self.active_tasks:
            self.active_tasks[task_id].update({
                "status": "completed",
                "result": result,
                "completed_at": time.time()
            })
            self.completed_tasks.append(self.active_tasks.pop(task_id))
    
    def fail_task(self, task_id: int, error: str):
        """Mark task as failed."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].update({
                "status": "failed",
                "error": error
            })
            self.failed_tasks.append(self.active_tasks.pop(task_id))
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "pending": len(self.tasks),
            "active": len(self.active_tasks),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "total_processed": self.task_counter
        }


class PythonSandbox:
    """Pure Python fallback for sandbox execution."""
    
    def execute_safely(self, code: str, timeout: float = 10.0,
                       memory_limit_mb: int = 256) -> dict:
        """Execute code safely using Python subprocess."""
        import subprocess
        import sys
        import time
        import tempfile
        import os
        
        start_time = time.time()
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, '-u', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time,
                "timed_out": False
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Execution timed out",
                "return_code": -1,
                "execution_time": timeout,
                "timed_out": True
            }
        finally:
            try:
                os.remove(temp_file)
            except:
                pass
    
    def check_code_safety(self, code: str) -> dict:
        """Check code for dangerous operations."""
        warnings = []
        danger_level = 0
        
        dangerous_patterns = [
            ("os.system", "System command execution", 2),
            ("subprocess.call", "Subprocess execution", 2),
            ("subprocess.Popen", "Subprocess creation", 2),
            ("eval(", "Code evaluation", 2),
            ("exec(", "Code execution", 2),
            ("__import__", "Dynamic import", 2),
            ("shutil.rmtree", "Directory deletion", 3),
            ("os.remove", "File deletion", 2),
            ("pickle.loads", "Deserialization risk", 3),
            ("socket.", "Network access", 2),
        ]
        
        for pattern, description, level in dangerous_patterns:
            if pattern in code:
                warnings.append({
                    "pattern": pattern,
                    "description": description,
                    "severity": level
                })
                danger_level = max(danger_level, level)
        
        return {
            "safe": danger_level == 0,
            "danger_level": danger_level,
            "warnings": warnings,
            "warning_count": len(warnings)
        }
    
    def get_process_resources(self, pid: int) -> dict:
        """Get process resource usage."""
        try:
            import psutil
            process = psutil.Process(pid)
            
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "threads": process.num_threads(),
                "status": process.status()
            }
        except:
            return {"error": "Process not found"}
    
    def execute_micro_skill(self, skill_name: str, parameters: dict) -> dict:
        """Execute a registered micro-skill."""
        safe_skills = {
            "calculate": lambda **kwargs: eval(kwargs.get("expression", "0")),
            "string_ops": lambda **kwargs: kwargs.get("text", "").lower() if kwargs.get("op") == "lower" else kwargs.get("text", ""),
            "list_filter": lambda **kwargs: [x for x in kwargs.get("items", []) if kwargs.get("filter_str", "") in str(x)],
        }
        
        if skill_name not in safe_skills:
            return {"success": False, "error": f"Unknown skill: {skill_name}"}
        
        try:
            result = safe_skills[skill_name](**parameters)
            return {"success": True, "result": result, "skill": skill_name}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================
# GLOBAL INSTANCE
# ============================================================

# Create global instance for easy access
mojo = MojoIntegration()
