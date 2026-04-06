# Self-Improvement System - Autonomous Code Generation & Agent Evolution

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from src.config.settings import MEMORY_DIR, PROJECT_ROOT
from src.ai_client import DualAIClient

class SelfImprovementEngine:
    """
    Autonomous system that improves itself outside of prompts by:
    1. Analyzing failures and generating code patches
    2. Creating new agent capabilities when needed
    3. Optimizing existing agent performance
    4. Evolving system architecture based on usage patterns
    """
    
    def __init__(self, ai_client: DualAIClient):
        self.ai_client = ai_client
        self.improvements_file = MEMORY_DIR / "self_improvements.json"
        self.improvements: List[Dict] = self._load_improvements()
        self.code_generation_log = MEMORY_DIR / "code_gen_log.json"
        
    def _load_improvements(self) -> List[Dict]:
        """Load improvement history."""
        if self.improvements_file.exists():
            with open(self.improvements_file, 'r') as f:
                return json.load(f)
        return []
    
    def analyze_and_improve(self, action_type: str, user_input: str, 
                           result: dict, error_context: dict = None) -> Dict:
        """
        Main improvement loop: analyze a failure and autonomously generate improvements.
        
        This is the core self-improvement mechanism - the system identifies weaknesses
        and generates code/prompt fixes without human intervention.
        """
        if result.get("status") == "success":
            return {"status": "no_improvement_needed", "reason": "Action succeeded"}
        
        improvement_id = f"imp_{datetime.now().strftime('%Y%m%d%H%M%S')}_{action_type}"
        
        # Step 1: Diagnose the problem
        diagnosis = self._diagnose_problem(action_type, user_input, result, error_context)
        
        # Step 2: Generate improvement strategy
        improvement_strategy = self._generate_improvement_strategy(diagnosis)
        
        # Step 3: Execute improvement (generate code, update prompts, etc.)
        execution_result = self._execute_improvement(improvement_strategy)
        
        # Step 4: Record the improvement
        improvement_record = {
            "id": improvement_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "diagnosis": diagnosis,
            "strategy": improvement_strategy,
            "execution_result": execution_result,
            "status": "applied" if execution_result.get("success") else "failed"
        }
        
        self.improvements.append(improvement_record)
        self._save_improvements()
        
        return improvement_record
    
    def _diagnose_problem(self, action_type: str, user_input: str, 
                          result: dict, error_context: dict = None) -> Dict:
        """Diagnose why an action failed."""
        error = result.get("error", "Unknown error")
        
        diagnosis = {
            "action_type": action_type,
            "user_input": user_input,
            "error": error,
            "error_context": error_context,
            "root_cause": self._identify_root_cause(action_type, error),
            "severity": self._assess_severity(error),
            "fixable_automatically": self._is_fixable_automatically(action_type, error)
        }
        
        return diagnosis
    
    def _identify_root_cause(self, action_type: str, error: str) -> str:
        """Identify the root cause of a failure."""
        error_lower = error.lower()
        
        # PC Control errors
        if action_type == "pc_control":
            if "not found" in error_lower or "doesn't exist" in error_lower:
                return "missing_resource"
            elif "permission" in error_lower or "denied" in error_lower:
                return "permission_issue"
            elif "timeout" in error_lower:
                return "timeout_issue"
            else:
                return "unclear_parameters"
        
        # File System errors
        elif action_type == "file_system":
            if "not found" in error_lower or "no such file" in error_lower:
                return "missing_file"
            elif "permission" in error_lower or "access denied" in error_lower:
                return "permission_issue"
            elif "directory" in error_lower:
                return "path_issue"
            else:
                return "invalid_operation"
        
        # Browser errors
        elif action_type == "browser":
            if "timeout" in error_lower:
                return "timeout_issue"
            elif "not found" in error_lower or "no element" in error_lower:
                return "missing_selector"
            elif "navigation" in error_lower:
                return "url_issue"
            else:
                return "browser_error"
        
        return "unknown_cause"
    
    def _assess_severity(self, error: str) -> str:
        """Assess the severity of an error."""
        error_lower = error.lower()
        
        if "critical" in error_lower or "fatal" in error_lower:
            return "critical"
        elif "permission" in error_lower or "denied" in error_lower:
            return "high"
        elif "timeout" in error_lower:
            return "medium"
        else:
            return "low"
    
    def _is_fixable_automatically(self, action_type: str, error: str) -> bool:
        """Determine if the issue can be fixed automatically."""
        # These types of errors can typically be auto-fixed
        auto_fixable = [
            "missing_selector",
            "unclear_parameters",
            "invalid_operation",
            "timeout_issue"
        ]
        
        root_cause = self._identify_root_cause(action_type, error)
        return root_cause in auto_fixable
    
    def _generate_improvement_strategy(self, diagnosis: Dict) -> Dict:
        """Generate a strategy for improving the system based on diagnosis."""
        action_type = diagnosis["action_type"]
        root_cause = diagnosis["root_cause"]
        
        strategy = {
            "type": "unknown",
            "description": "",
            "actions": []
        }
        
        if root_cause == "unclear_parameters" or root_cause == "missing_selector":
            strategy = {
                "type": "prompt_enhancement",
                "description": f"Enhance prompt for {action_type} to better extract parameters",
                "actions": [
                    "Update prompt template with better examples",
                    "Add parameter validation logic",
                    "Implement fallback strategies"
                ]
            }
        elif root_cause == "permission_issue":
            strategy = {
                "type": "error_handling",
                "description": f"Improve error handling for permission issues in {action_type}",
                "actions": [
                    "Add permission check before operations",
                    "Provide clearer error messages",
                    "Suggest alternative approaches"
                ]
            }
        elif root_cause == "timeout_issue":
            strategy = {
                "type": "performance_optimization",
                "description": f"Optimize timeout handling for {action_type}",
                "actions": [
                    "Increase timeout limits",
                    "Implement retry logic",
                    "Add progress indicators"
                ]
            }
        elif root_cause in ["missing_file", "missing_resource"]:
            strategy = {
                "type": "resource_creation",
                "description": f"Add resource creation capability for {action_type}",
                "actions": [
                    "Generate code to create missing resources",
                    "Add validation before resource access",
                    "Implement graceful degradation"
                ]
            }
        else:
            strategy = {
                "type": "general_improvement",
                "description": f"General improvement for {action_type}",
                "actions": [
                    "Review and update prompts",
                    "Add better error handling",
                    "Implement logging for debugging"
                ]
            }
        
        return strategy
    
    def _execute_improvement(self, strategy: Dict) -> Dict:
        """Execute the improvement strategy."""
        improvement_type = strategy["type"]
        
        if improvement_type == "prompt_enhancement":
            return self._enhance_prompts(strategy)
        elif improvement_type == "error_handling":
            return self._improve_error_handling(strategy)
        elif improvement_type == "performance_optimization":
            return self._optimize_performance(strategy)
        elif improvement_type == "resource_creation":
            return self._create_resources(strategy)
        else:
            return self._apply_general_improvements(strategy)
    
    def _enhance_prompts(self, strategy: Dict) -> Dict:
        """Enhance prompt templates based on failures."""
        # Ask AI to generate improved prompts
        prompt = f"""
        Based on this failure analysis, generate an improved prompt template.
        
        Strategy: {strategy['description']}
        Actions needed: {', '.join(strategy['actions'])}
        
        Generate an improved prompt template that:
        1. Better guides the AI model
        2. Includes examples
        3. Has clearer instructions
        4. Handles edge cases
        
        Return ONLY the improved prompt template as a string.
        """
        
        improved_prompt = self.ai_client.generate_response(prompt, max_tokens=1024)
        
        return {
            "success": True,
            "improvement_type": "prompt_enhancement",
            "generated_content": improved_prompt,
            "applied": False  # Would need human review before applying
        }
    
    def _improve_error_handling(self, strategy: Dict) -> Dict:
        """Generate improved error handling code."""
        prompt = f"""
        Generate improved error handling code for this scenario:
        
        Strategy: {strategy['description']}
        Actions needed: {', '.join(strategy['actions'])}
        
        Generate Python code that:
        1. Checks for errors before operations
        2. Provides clear error messages
        3. Suggests alternatives when operations fail
        4. Logs errors for future analysis
        
        Return ONLY the Python code, properly formatted.
        """
        
        error_handling_code = self.ai_client.generate_response(prompt, max_tokens=2048)
        
        return {
            "success": True,
            "improvement_type": "error_handling",
            "generated_code": error_handling_code,
            "applied": False
        }
    
    def _optimize_performance(self, strategy: Dict) -> Dict:
        """Generate performance optimizations."""
        prompt = f"""
        Generate performance optimization suggestions for:
        
        Strategy: {strategy['description']}
        Actions needed: {', '.join(strategy['actions'])}
        
        Provide specific recommendations for:
        1. Timeout values
        2. Retry logic
        3. Progress indicators
        4. Resource management
        
        Return as a structured JSON object with specific values.
        """
        
        optimizations = self.ai_client.generate_response(prompt, max_tokens=1024)
        
        return {
            "success": True,
            "improvement_type": "performance_optimization",
            "recommendations": optimizations,
            "applied": False
        }
    
    def _create_resources(self, strategy: Dict) -> Dict:
        """Generate code to create missing resources."""
        prompt = f"""
        Generate code to automatically create missing resources:
        
        Strategy: {strategy['description']}
        Actions needed: {', '.join(strategy['actions'])}
        
        Generate Python functions that:
        1. Check if resource exists
        2. Create the resource if missing
        3. Validate the created resource
        4. Handle creation failures gracefully
        
        Return ONLY the Python code.
        """
        
        resource_code = self.ai_client.generate_response(prompt, max_tokens=2048)
        
        return {
            "success": True,
            "improvement_type": "resource_creation",
            "generated_code": resource_code,
            "applied": False
        }
    
    def _apply_general_improvements(self, strategy: Dict) -> Dict:
        """Apply general improvements to the system."""
        prompt = f"""
        Analyze this failure and suggest specific improvements:
        
        Strategy: {strategy['description']}
        Actions needed: {', '.join(strategy['actions'])}
        
        Provide concrete suggestions for:
        1. Prompt improvements
        2. Code changes
        3. Configuration updates
        4. New capabilities needed
        
        Return as structured JSON with specific recommendations.
        """
        
        suggestions = self.ai_client.generate_response(prompt, max_tokens=1536)
        
        return {
            "success": True,
            "improvement_type": "general_improvement",
            "suggestions": suggestions,
            "applied": False
        }
    
    def generate_new_agent_capability(self, capability_request: str) -> Dict:
        """
        Generate entirely new agent capabilities when existing ones are insufficient.
        This is the most advanced form of self-improvement - creating new code.
        """
        prompt = f"""
        The system needs a new capability: {capability_request}
        
        Generate a complete Python module that:
        1. Implements this new capability
        2. Follows the existing agent architecture
        3. Has proper error handling
        4. Includes documentation
        5. Can be integrated into the LangGraph orchestrator
        
        The module should be in a format ready to be saved as a Python file.
        
        Return ONLY the complete Python code.
        """
        
        new_capability_code = self.ai_client.generate_response(prompt, max_tokens=4096)
        
        improvement_record = {
            "id": f"new_cap_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": "new_capability",
            "request": capability_request,
            "generated_code": new_capability_code,
            "status": "generated",
            "requires_review": True
        }
        
        self.improvements.append(improvement_record)
        self._save_improvements()
        
        # Log the code generation
        self._log_code_generation(capability_request, new_capability_code)
        
        return improvement_record
    
    def _log_code_generation(self, request: str, code: str):
        """Log generated code for tracking."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "code_length": len(code),
            "status": "generated"
        }
        
        log_file = self.code_generation_log
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_improvement_summary(self) -> Dict:
        """Get a summary of all improvements made."""
        total = len(self.improvements)
        applied = sum(1 for i in self.improvements if i.get("status") == "applied")
        pending = sum(1 for i in self.improvements if i.get("status") == "generated")
        
        return {
            "total_improvements": total,
            "applied": applied,
            "pending_review": pending,
            "recent_improvements": self.improvements[-5:] if self.improvements else [],
            "learning_rate": applied / max(1, total) * 100 if total > 0 else 0
        }
    
    def _save_improvements(self):
        """Save improvements to disk."""
        self.improvements_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.improvements_file, 'w') as f:
            json.dump(self.improvements, f, indent=2)
    
    def apply_improvement(self, improvement_id: str, code_path: str = None) -> Dict:
        """Apply a pending improvement (requires human review for code changes)."""
        for improvement in self.improvements:
            if improvement["id"] == improvement_id:
                if code_path and "generated_code" in improvement:
                    # Save the generated code to the specified path
                    path = Path(code_path)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with open(path, 'w') as f:
                        f.write(improvement["generated_code"])
                    
                    improvement["status"] = "applied"
                    improvement["applied_path"] = str(path)
                    self._save_improvements()
                    
                    return {
                        "status": "success",
                        "message": f"Improvement applied to {path}",
                        "improvement_id": improvement_id
                    }
                
                return {
                    "status": "error",
                    "error": "No code to apply or missing code path"
                }
        
        return {
            "status": "error",
            "error": f"Improvement {improvement_id} not found"
        }
