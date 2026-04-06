# Reinforcement Learning System - Prompt Optimization via Feedback

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.config.settings import MEMORY_DIR

class PromptOptimizer:
    """
    Reinforcement Learning system that learns from user feedback to optimize prompts.
    
    Uses a reward-based system where:
    - Successful actions increase prompt weights
    - Failed actions decrease prompt weights
    - User feedback directly influences future prompt selection
    """
    
    def __init__(self):
        self.memory_file = MEMORY_DIR / "rl_memory.json"
        self.prompt_templates_file = MEMORY_DIR / "prompt_templates.json"
        self.rl_memory: Dict = self._load_memory()
        self.prompt_templates: Dict = self._load_prompt_templates()
        
    def _load_memory(self) -> Dict:
        """Load RL memory from disk."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {
            "action_history": [],
            "feedback_history": [],
            "prompt_performance": {},
            "total_interactions": 0,
            "successful_actions": 0,
            "failed_actions": 0
        }
    
    def _load_prompt_templates(self) -> Dict:
        """Load prompt templates from disk."""
        if self.prompt_templates_file.exists():
            with open(self.prompt_templates_file, 'r') as f:
                return json.load(f)
        return {
            "pc_control": {
                "base_template": "The user wants to control their PC. Based on their request, what specific action should be taken?\n\nAvailable actions: {actions}\n\nUser request: {user_input}\n\nRespond with a JSON object: {{\"action\": \"action_name\", \"parameters\": {{}}}}",
                "weight": 1.0,
                "success_count": 0,
                "failure_count": 0
            },
            "file_system": {
                "base_template": "The user wants to perform a file system operation. Based on their request, what specific action should be taken?\n\nAvailable actions: {actions}\n\nUser request: {user_input}\n\nRespond with a JSON object: {{\"action\": \"action_name\", \"parameters\": {{}}}}",
                "weight": 1.0,
                "success_count": 0,
                "failure_count": 0
            },
            "browser": {
                "base_template": "The user wants to browse the web. Based on their request, what should I do?\n\nAvailable actions: {actions}\n\nUser request: {user_input}\n\nRespond with a JSON object: {{\"action\": \"action_name\", \"parameters\": {{}}}}",
                "weight": 1.0,
                "success_count": 0,
                "failure_count": 0
            },
            "general": {
                "base_template": "The user has made a request: {user_input}\n\nAnalyze this request and determine the best course of action.\n\nRespond with a clear explanation and, if needed, a JSON action block.",
                "weight": 1.0,
                "success_count": 0,
                "failure_count": 0
            }
        }
    
    def record_action(self, action_type: str, user_input: str, ai_response: str, 
                     action_result: dict, execution_time: float = 0.0) -> str:
        """
        Record an action and its result for learning.
        
        Returns a unique interaction ID.
        """
        interaction_id = f"int_{self.rl_memory['total_interactions'] + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        action_record = {
            "id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "user_input": user_input,
            "ai_response": ai_response,
            "action_result": action_result,
            "execution_time": execution_time,
            "reward": 0.0,  # Will be set when feedback is provided
            "feedback_provided": False
        }
        
        self.rl_memory["action_history"].append(action_record)
        self.rl_memory["total_interactions"] += 1
        
        # Update performance tracking
        if action_type not in self.rl_memory["prompt_performance"]:
            self.rl_memory["prompt_performance"][action_type] = {
                "total": 0,
                "success": 0,
                "failure": 0,
                "avg_reward": 0.0
            }
        
        self.rl_memory["prompt_performance"][action_type]["total"] += 1
        
        self._save_memory()
        return interaction_id
    
    def provide_feedback(self, interaction_id: str, success: bool, 
                        feedback_text: str = "", reward: float = None) -> dict:
        """
        Provide feedback on a previous action.
        
        This is the core of the reinforcement learning - the system learns
        from explicit user feedback about whether actions succeeded or failed.
        """
        # Find the interaction
        interaction = None
        for action in self.rl_memory["action_history"]:
            if action["id"] == interaction_id:
                interaction = action
                break
        
        if not interaction:
            return {"status": "error", "error": "Interaction not found"}
        
        # Calculate reward
        if reward is None:
            reward = 1.0 if success else -1.0
        
        # Adjust reward based on execution time (faster = better)
        if interaction["execution_time"] > 0:
            time_bonus = max(0, 1.0 - (interaction["execution_time"] / 60.0))  # Normalize to 60s
            reward += time_bonus * 0.2  # Up to 20% bonus for speed
        
        # Update the interaction
        interaction["reward"] = reward
        interaction["feedback_provided"] = True
        interaction["user_feedback"] = feedback_text
        
        # Update performance stats
        action_type = interaction["action_type"]
        if action_type in self.rl_memory["prompt_performance"]:
            perf = self.rl_memory["prompt_performance"][action_type]
            perf["success" if success else "failure"] += 1
            
            # Update average reward
            total_reward = sum(
                a["reward"] for a in self.rl_memory["action_history"]
                if a["action_type"] == action_type and a["feedback_provided"]
            )
            perf["avg_reward"] = total_reward / max(1, sum(
                1 for a in self.rl_memory["action_history"]
                if a["action_type"] == action_type and a["feedback_provided"]
            ))
        
        # Update prompt template weights based on success
        self._update_prompt_weights(action_type, success)
        
        if success:
            self.rl_memory["successful_actions"] += 1
        else:
            self.rl_memory["failed_actions"] += 1
        
        self.rl_memory["feedback_history"].append({
            "interaction_id": interaction_id,
            "success": success,
            "reward": reward,
            "feedback_text": feedback_text,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_memory()
        
        return {
            "status": "success",
            "interaction_id": interaction_id,
            "reward": reward,
            "new_weight": self.prompt_templates.get(action_type, {}).get("weight", 1.0)
        }
    
    def _update_prompt_weights(self, action_type: str, success: bool):
        """Update prompt template weights based on feedback."""
        if action_type in self.prompt_templates:
            template = self.prompt_templates[action_type]
            if success:
                template["success_count"] += 1
                # Increase weight for successful actions
                template["weight"] = min(3.0, template["weight"] * 1.1)  # Cap at 3.0
            else:
                template["failure_count"] += 1
                # Decrease weight for failed actions
                template["weight"] = max(0.1, template["weight"] * 0.9)  # Floor at 0.1
    
    def get_optimized_prompt(self, action_type: str, **kwargs) -> str:
        """
        Get the best prompt template for a given action type,
        weighted by historical performance.
        """
        if action_type in self.prompt_templates:
            template = self.prompt_templates[action_type]
            # Return the template with kwargs substituted
            try:
                return template["base_template"].format(**kwargs)
            except KeyError:
                return template["base_template"].format(
                    user_input=kwargs.get("user_input", ""),
                    actions=kwargs.get("actions", "")
                )
        
        # Fallback to general template
        return self.prompt_templates["general"]["base_template"].format(**kwargs)
    
    def get_learning_insights(self) -> dict:
        """Get insights from the learning system."""
        total = self.rl_memory["total_interactions"]
        if total == 0:
            return {
                "total_interactions": 0,
                "success_rate": 0.0,
                "insights": ["No interactions yet. Start using SIGRID to enable learning."]
            }
        
        success_rate = self.rl_memory["successful_actions"] / max(1, total) * 100
        
        insights = []
        
        # Identify best performing action types
        if self.rl_memory["prompt_performance"]:
            best_type = max(
                self.rl_memory["prompt_performance"].items(),
                key=lambda x: x[1].get("avg_reward", 0)
            )
            insights.append(f"Best performing: {best_type[0]} (avg reward: {best_type[1].get('avg_reward', 0):.2f})")
            
            worst_type = min(
                self.rl_memory["prompt_performance"].items(),
                key=lambda x: x[1].get("avg_reward", 0)
            )
            insights.append(f"Needs improvement: {worst_type[0]} (avg reward: {worst_type[1].get('avg_reward', 0):.2f})")
        
        # Identify patterns in failures
        failed_actions = [
            a for a in self.rl_memory["action_history"]
            if not a.get("action_result", {}).get("status") == "success"
        ]
        if failed_actions:
            insights.append(f"Found {len(failed_actions)} failed actions that need prompt optimization")
        
        return {
            "total_interactions": total,
            "successful_actions": self.rl_memory["successful_actions"],
            "failed_actions": self.rl_memory["failed_actions"],
            "success_rate": success_rate,
            "prompt_performance": self.rl_memory["prompt_performance"],
            "insights": insights
        }
    
    def analyze_failures(self) -> List[Dict]:
        """Analyze past failures to identify patterns."""
        failures = [
            a for a in self.rl_memory["action_history"]
            if a.get("action_result", {}).get("status") != "success"
        ]
        
        analysis = []
        for failure in failures:
            analysis.append({
                "action_type": failure["action_type"],
                "user_input": failure["user_input"],
                "error": failure["action_result"].get("error", "Unknown error"),
                "timestamp": failure["timestamp"],
                "suggestion": self._generate_failure_suggestion(failure)
            })
        
        return analysis
    
    def _generate_failure_suggestion(self, failure: Dict) -> str:
        """Generate a suggestion for improving a failed action."""
        action_type = failure["action_type"]
        error = failure["action_result"].get("error", "")
        
        suggestions = {
            "pc_control": "Try being more specific about the action parameters",
            "file_system": "Check file paths and permissions",
            "browser": "Ensure the website is accessible and selectors are correct",
            "general": "Provide more detailed instructions"
        }
        
        return suggestions.get(action_type, "Review and refine the prompt")
    
    def _save_memory(self):
        """Save RL memory to disk."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.rl_memory, f, indent=2)
        
        # Also save prompt templates
        with open(self.prompt_templates_file, 'w') as f:
            json.dump(self.prompt_templates, f, indent=2)
    
    def reset_learning(self):
        """Reset all learning data."""
        self.rl_memory = {
            "action_history": [],
            "feedback_history": [],
            "prompt_performance": {},
            "total_interactions": 0,
            "successful_actions": 0,
            "failed_actions": 0
        }
        self._load_prompt_templates()  # Reset to defaults
        self._save_memory()
        return {"status": "success", "message": "Learning system reset"}
