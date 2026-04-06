# LangGraph Orchestrator - Main Agent Coordination System with Learning

from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
import json
import time

# Import specialized agents
from src.ai_client import DualAIClient
from src.modules.pc_control import PCController
from src.modules.file_system import FileSystemAgent
from src.modules.browser import BrowserAgentSync
from src.learning.prompt_optimizer import PromptOptimizer
from src.learning.self_improvement import SelfImprovementEngine

class AgentState(TypedDict):
    """State schema for the LangGraph workflow."""
    user_input: str
    ai_response: str
    agent_actions: Annotated[List[dict], operator.add]
    current_agent: str
    conversation_history: Annotated[List[dict], operator.add]
    needs_pc_control: bool
    needs_file_operation: bool
    needs_browser: bool
    needs_terminal: bool
    screenshot_path: Optional[str]
    error: Optional[str]
    iteration_count: int
    interaction_id: Optional[str]
    use_qwen: bool

class SigridOrchestrator:
    """
    Main orchestrator that coordinates all specialized agents.
    
    Integrated with:
    - Dual AI Engine (Google Gemma 4 + Qwen CLI)
    - Reinforcement Learning (Prompt Optimization)
    - Self-Improvement Engine (Autonomous code evolution)
    """
    
    def __init__(self):
        self.ai_client = DualAIClient()
        self.pc_controller = PCController()
        self.file_system = FileSystemAgent()
        self.browser = None  # Lazy initialization
        
        # Learning systems
        self.prompt_optimizer = PromptOptimizer()
        self.self_improvement = SelfImprovementEngine(self.ai_client)
        
        # Initialize LangGraph workflow
        self.workflow = self._build_workflow()
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        # Set up system prompt
        self.ai_client.initialize_system_prompt(self._get_system_prompt())
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI."""
        return """You are SIGRID (Self-Improving Generative Reasoning & Intelligent Decision system), 
an advanced AI assistant with self-learning capabilities that controls a computer system.

CAPABILITIES:
1. FILE SYSTEM: Read, write, search, copy, move, delete files and directories
2. PC CONTROL: Move mouse, click, type, take screenshots, control keyboard
3. BROWSER: Navigate websites, click elements, fill forms, extract content
4. TERMINAL: Execute system commands
5. SELF-LEARNING: You improve your own performance through feedback analysis

RESPONSE FORMAT:
When you need to perform an action, respond with a JSON object in this format:
```json
{
  "agent": "pc_control" | "file_system" | "browser" | "orchestrator",
  "action": "action_name",
  "parameters": {"param1": "value1"},
  "explanation": "What you're doing and why"
}
```

Always explain what you're doing in natural language, but include the JSON action block when you need to perform system operations.

LEARNING BEHAVIOR:
- When an action fails, analyze why and suggest improvements
- Learn from user feedback to optimize future responses
- Track which approaches work best for different types of requests

SAFETY RULES:
- Always confirm destructive actions (delete, etc.)
- Never execute dangerous commands without user confirmation
- Provide clear explanations of what you're about to do
- If unsure, ask for clarification"""
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("route", self._route_node)
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("pc_control", self._pc_control_node)
        workflow.add_node("file_system", self._file_system_node)
        workflow.add_node("browser", self._browser_node)
        workflow.add_node("respond", self._respond_node)
        
        # Define edges
        workflow.set_entry_point("route")
        
        workflow.add_conditional_edges(
            "route",
            self._route_decision,
            {
                "orchestrator": "orchestrator",
                "pc_control": "pc_control",
                "file_system": "file_system",
                "browser": "browser",
            }
        )
        
        workflow.add_edge("orchestrator", "respond")
        workflow.add_edge("pc_control", "respond")
        workflow.add_edge("file_system", "respond")
        workflow.add_edge("browser", "respond")
        workflow.add_edge("respond", END)
        
        return workflow
    
    def _route_node(self, state: AgentState) -> dict:
        """Route the user input to the appropriate agent."""
        # Use AI to determine which agent should handle the request
        response = self.ai_client.chat_message(
            f"Based on this user input, which agent should handle it? Respond with ONLY one word: orchestrator, pc_control, file_system, or browser.\n\n"
            f"User: {state['user_input']}"
        )
        
        agent = response.strip().lower()
        if "pc_control" in agent or "mouse" in agent or "keyboard" in agent or "screen" in agent:
            agent_type = "pc_control"
        elif "file" in agent or "folder" in agent or "directory" in agent:
            agent_type = "file_system"
        elif "browser" in agent or "web" in agent or "website" in agent or "url" in agent:
            agent_type = "browser"
        else:
            agent_type = "orchestrator"
        
        return {
            "current_agent": agent_type,
            "needs_pc_control": agent_type == "pc_control",
            "needs_file_operation": agent_type == "file_system",
            "needs_browser": agent_type == "browser",
        }
    
    def _route_decision(self, state: AgentState) -> str:
        """Decide which agent to route to."""
        return state["current_agent"]
    
    def _orchestrator_node(self, state: AgentState) -> dict:
        """Orchestrator node - handles general conversation."""
        response = self.ai_client.chat_message(state["user_input"], use_qwen=state.get("use_qwen", False))
        
        # Extract any function calls from the response
        actions = self.ai_client.extract_function_calls(response)
        
        return {
            "ai_response": response,
            "agent_actions": actions,
            "conversation_history": [{"role": "user", "content": state["user_input"]}, {"role": "assistant", "content": response}]
        }
    
    def _pc_control_node(self, state: AgentState) -> dict:
        """PC Control agent node with learning integration."""
        start_time = time.time()
        
        # Get optimized prompt from RL system
        optimized_prompt = self.prompt_optimizer.get_optimized_prompt(
            "pc_control",
            user_input=state["user_input"],
            actions="move_mouse, click, double_click, right_click, scroll, drag_to, type_text, press_key, hotkey, get_mouse_position, get_screen_size, take_screenshot, locate_on_screen"
        )
        
        response = self.ai_client.chat_message(optimized_prompt, use_qwen=state.get("use_qwen", False))
        
        # Parse the action
        try:
            # Extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            action_data = json.loads(json_str)
            action_name = action_data.get("action")
            parameters = action_data.get("parameters", {})
            
            # Execute the action
            result = self.pc_controller.execute_action(action_name, **parameters)
            execution_time = time.time() - start_time
            
            # Record action in RL system
            interaction_id = self.prompt_optimizer.record_action(
                action_type="pc_control",
                user_input=state["user_input"],
                ai_response=response,
                action_result=result,
                execution_time=execution_time
            )
            
            # If action failed, trigger self-improvement
            if result.get("status") != "success":
                self.self_improvement.analyze_and_improve(
                    action_type="pc_control",
                    user_input=state["user_input"],
                    result=result
                )
            
            # Get AI's explanation
            explanation = self.ai_client.chat_message(
                f"I executed the action: {action_name} with parameters: {parameters}. Result: {result}. "
                f"Explain what was done in a friendly way."
            )
            
            response_data = {
                "ai_response": explanation,
                "agent_actions": [{"action": action_name, "result": result, "agent": "pc_control"}],
                "interaction_id": interaction_id,
                "conversation_history": [{"role": "assistant", "content": explanation}]
            }
            
            if result.get("status") == "success" and action_name == "take_screenshot":
                response_data["screenshot_path"] = result.get("path")
            
            return response_data
        except Exception as e:
            # Record failure for learning
            interaction_id = self.prompt_optimizer.record_action(
                action_type="pc_control",
                user_input=state["user_input"],
                ai_response=response,
                action_result={"status": "error", "error": str(e)},
                execution_time=time.time() - start_time
            )
            
            # Trigger self-improvement
            self.self_improvement.analyze_and_improve(
                action_type="pc_control",
                user_input=state["user_input"],
                result={"status": "error", "error": str(e)}
            )
            
            return {
                "ai_response": f"I encountered an error trying to control the PC: {str(e)}",
                "agent_actions": [{"action": "error", "error": str(e), "agent": "pc_control"}],
                "interaction_id": interaction_id,
                "error": str(e),
                "conversation_history": [{"role": "assistant", "content": f"Error: {str(e)}"}]
            }
    
    def _file_system_node(self, state: AgentState) -> dict:
        """File System agent node with learning integration."""
        start_time = time.time()
        
        # Get optimized prompt
        optimized_prompt = self.prompt_optimizer.get_optimized_prompt(
            "file_system",
            user_input=state["user_input"],
            actions="read_file, write_file, append_file, delete_file, list_directory, create_directory, delete_directory, copy_file, move_file, search_files, get_file_info"
        )
        
        response = self.ai_client.chat_message(optimized_prompt, use_qwen=state.get("use_qwen", False))
        
        try:
            # Extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            action_data = json.loads(json_str)
            action_name = action_data.get("action")
            parameters = action_data.get("parameters", {})
            
            # Execute the action
            result = self.file_system.execute_action(action_name, **parameters)
            execution_time = time.time() - start_time
            
            # Record in RL system
            interaction_id = self.prompt_optimizer.record_action(
                action_type="file_system",
                user_input=state["user_input"],
                ai_response=response,
                action_result=result,
                execution_time=execution_time
            )
            
            # Trigger self-improvement on failure
            if result.get("status") != "success":
                self.self_improvement.analyze_and_improve(
                    action_type="file_system",
                    user_input=state["user_input"],
                    result=result
                )
            
            # Get AI's explanation
            explanation = self.ai_client.chat_message(
                f"I executed the file action: {action_name} with parameters: {parameters}. Result: {result}. "
                f"Explain what was done clearly."
            )
            
            return {
                "ai_response": explanation,
                "agent_actions": [{"action": action_name, "result": result, "agent": "file_system"}],
                "interaction_id": interaction_id,
                "conversation_history": [{"role": "assistant", "content": explanation}]
            }
        except Exception as e:
            interaction_id = self.prompt_optimizer.record_action(
                action_type="file_system",
                user_input=state["user_input"],
                ai_response=response,
                action_result={"status": "error", "error": str(e)},
                execution_time=time.time() - start_time
            )
            
            self.self_improvement.analyze_and_improve(
                action_type="file_system",
                user_input=state["user_input"],
                result={"status": "error", "error": str(e)}
            )
            
            return {
                "ai_response": f"I encountered an error with the file system: {str(e)}",
                "agent_actions": [{"action": "error", "error": str(e), "agent": "file_system"}],
                "interaction_id": interaction_id,
                "error": str(e),
                "conversation_history": [{"role": "assistant", "content": f"Error: {str(e)}"}]
            }
    
    def _browser_node(self, state: AgentState) -> dict:
        """Browser agent node with learning integration."""
        start_time = time.time()
        
        if not self.browser:
            self.browser = BrowserAgentSync()
            self.browser.initialize()
        
        # Get optimized prompt
        optimized_prompt = self.prompt_optimizer.get_optimized_prompt(
            "browser",
            user_input=state["user_input"],
            actions="navigate, click, fill, get_page_content, screenshot, get_all_links"
        )
        
        response = self.ai_client.chat_message(optimized_prompt, use_qwen=state.get("use_qwen", False))
        
        try:
            # Extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            action_data = json.loads(json_str)
            action_name = action_data.get("action")
            parameters = action_data.get("parameters", {})
            
            # Execute the action
            result = self.browser.execute_action(action_name, **parameters)
            execution_time = time.time() - start_time
            
            # Record in RL system
            interaction_id = self.prompt_optimizer.record_action(
                action_type="browser",
                user_input=state["user_input"],
                ai_response=response,
                action_result=result,
                execution_time=execution_time
            )
            
            # Trigger self-improvement on failure
            if result.get("status") != "success":
                self.self_improvement.analyze_and_improve(
                    action_type="browser",
                    user_input=state["user_input"],
                    result=result
                )
            
            explanation = self.ai_client.chat_message(
                f"I executed the browser action: {action_name} with parameters: {parameters}. Result: {result}. "
                f"Explain what was done."
            )
            
            return {
                "ai_response": explanation,
                "agent_actions": [{"action": action_name, "result": result, "agent": "browser"}],
                "interaction_id": interaction_id,
                "conversation_history": [{"role": "assistant", "content": explanation}]
            }
        except Exception as e:
            interaction_id = self.prompt_optimizer.record_action(
                action_type="browser",
                user_input=state["user_input"],
                ai_response=response,
                action_result={"status": "error", "error": str(e)},
                execution_time=time.time() - start_time
            )
            
            self.self_improvement.analyze_and_improve(
                action_type="browser",
                user_input=state["user_input"],
                result={"status": "error", "error": str(e)}
            )
            
            return {
                "ai_response": f"I encountered an error with the browser: {str(e)}",
                "agent_actions": [{"action": "error", "error": str(e), "agent": "browser"}],
                "interaction_id": interaction_id,
                "error": str(e),
                "conversation_history": [{"role": "assistant", "content": f"Error: {str(e)}"}]
            }
    
    def _respond_node(self, state: AgentState) -> dict:
        """Final response node - formats the response."""
        return {
            "ai_response": state.get("ai_response", "I'm sorry, I couldn't process that request."),
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    def process_input(self, user_input: str, thread_id: str = "default", use_qwen: bool = False) -> dict:
        """
        Process user input through the LangGraph workflow.
        
        Args:
            user_input: The user's request
            thread_id: Conversation thread identifier
            use_qwen: Whether to use Qwen CLI instead of Google AI
        """
        initial_state = {
            "user_input": user_input,
            "ai_response": "",
            "agent_actions": [],
            "current_agent": "",
            "conversation_history": [],
            "needs_pc_control": False,
            "needs_file_operation": False,
            "needs_browser": False,
            "needs_terminal": False,
            "screenshot_path": None,
            "error": None,
            "iteration_count": 0,
            "interaction_id": None,
            "use_qwen": use_qwen
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        result = self.app.invoke(initial_state, config)
        
        return result
    
    def provide_feedback(self, interaction_id: str, success: bool, feedback_text: str = "") -> dict:
        """Provide feedback on a previous interaction for RL."""
        return self.prompt_optimizer.provide_feedback(
            interaction_id=interaction_id,
            success=success,
            feedback_text=feedback_text
        )
    
    def get_learning_status(self) -> dict:
        """Get the current learning system status."""
        rl_insights = self.prompt_optimizer.get_learning_insights()
        improvement_summary = self.self_improvement.get_improvement_summary()
        
        return {
            "reinforcement_learning": rl_insights,
            "self_improvement": improvement_summary,
            "ai_engines": self.ai_client.get_ai_status()
        }
    
    def cleanup(self):
        """Clean up resources."""
        if self.browser:
            self.browser.close()
