# SIGRID High-Performance Task Queue Orchestrator (Mojo)
#
# Manages task scheduling between GUI, LLM, and execution agents.
# Optimized for low-latency task routing and priority management.
#
# Usage from Python:
#   import max.mojo.importer
#   from src.mojo import task_queue
#   queue = task_queue.TaskQueue()
#   queue.add_task("high", "pc_control", "take_screenshot")
#   task = queue.get_next_task()

from python import PythonObject
from python.python import *

# ============================================================
# PRIORITY TASK QUEUE
# ============================================================

@value
struct Task:
    """A task in the queue."""
    var priority: Int
    var agent_type: String
    var action: String
    var parameters: PythonObject
    var timestamp: Float
    var timeout: Float
    var retry_count: Int
    var status: String
    
    fn __init__(inout self, priority: Int, agent_type: String, action: String,
                parameters: PythonObject, timeout: Float = 30.0, retry_count: Int = 3):
        self.priority = priority
        self.agent_type = agent_type
        self.action = action
        self.parameters = parameters
        self.timestamp = Python.eval("time.time()")
        self.timeout = timeout
        self.retry_count = retry_count
        self.status = "pending"


struct TaskQueue:
    """
    High-priority task queue for SIGRID agent coordination.
    
    Priority levels:
    0 = Critical (system safety, emergency stop)
    1 = High (user-initiated actions)
    2 = Normal (background tasks)
    3 = Low (self-improvement, learning)
    """
    var tasks: PythonObject
    var max_size: Int
    var active_tasks: PythonObject
    var completed_tasks: PythonObject
    var failed_tasks: PythonObject
    var task_counter: Int
    
    fn __init__(inout self, max_size: Int = 1000):
        self.tasks = Python.list()  # Heap-based priority queue
        self.max_size = max_size
        self.active_tasks = Python.dict()
        self.completed_tasks = Python.list()
        self.failed_tasks = Python.list()
        self.task_counter = 0
    
    fn add_task(inout self, priority: Int, agent_type: String, action: String,
                parameters: PythonObject, timeout: Float = 30.0, retry_count: Int = 3) -> Int:
        """
        Add a task to the queue.
        Returns task ID.
        """
        if len(self.tasks) >= self.max_size:
            Python.eval("raise Exception('Task queue is full')")
            return -1
        
        let task = Task(priority, agent_type, action, parameters, timeout, retry_count)
        let task_id = self.task_counter
        self.task_counter += 1
        
        # Insert in priority order (lower number = higher priority)
        self.tasks.append(Python.tuple(priority, task_id, task))
        self.tasks.sort()  # Sort by priority
        
        return task_id
    
    fn get_next_task(self) -> PythonObject:
        """Get the highest priority task."""
        if len(self.tasks) == 0:
            return Python.None()
        
        let priority, task_id, task = self.tasks.pop(0)
        
        # Mark as active
        self.active_tasks[task_id] = Python.dict(
            Python.tuple(Python.eval("\"task_id\""), task_id),
            Python.tuple(Python.eval("\"status\""), "active"),
            Python.tuple(Python.eval("\"started_at\""), Python.eval("time.time()"))
        )
        
        return Python.dict(
            Python.tuple(Python.eval("\"task_id\""), task_id),
            Python.tuple(Python.eval("\"agent_type\""), task.agent_type),
            Python.tuple(Python.eval("\"action\""), task.action),
            Python.tuple(Python.eval("\"parameters\""), task.parameters),
            Python.tuple(Python.eval("\"timeout\""), task.timeout),
            Python.tuple(Python.eval("\"retry_count\""), task.retry_count)
        )
    
    fn complete_task(inout self, task_id: Int, result: PythonObject):
        """Mark a task as completed."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            self.active_tasks[task_id]["completed_at"] = Python.eval("time.time()")
            
            self.completed_tasks.append(self.active_tasks.pop(task_id))
    
    fn fail_task(inout self, task_id: Int, error: String):
        """Mark a task as failed."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = error
            
            self.failed_tasks.append(self.active_tasks.pop(task_id))
    
    fn get_queue_stats(self) -> PythonObject:
        """Get queue statistics."""
        return Python.dict(
            Python.tuple(Python.eval("\"pending\""), len(self.tasks)),
            Python.tuple(Python.eval("\"active\""), len(self.active_tasks)),
            Python.tuple(Python.eval("\"completed\""), len(self.completed_tasks)),
            Python.tuple(Python.eval("\"failed\""), len(self.failed_tasks)),
            Python.tuple(Python.eval("\"total_processed\""), self.task_counter)
        )
    
    fn clear_completed(self):
        """Clear completed and failed task history."""
        self.completed_tasks.clear()
        self.failed_tasks.clear()


# ============================================================
# AGENT COORDINATION
# ============================================================

fn coordinate_agents(agent_status: PythonObject) -> PythonObject:
    """
    Determine optimal agent routing based on current system state.
    Fast decision-making in Mojo for low-latency routing.
    """
    var routing_decision = Python.dict()
    
    # Check agent availability and load
    let available_agents = Python.list()
    for agent_name in agent_status.keys():
        if agent_status[agent_name]["available"] and agent_status[agent_name]["load"] < 0.8:
            available_agents.append(agent_name)
    
    routing_decision["available_agents"] = available_agents
    routing_decision["recommended_agent"] = available_agents[0] if len(available_agents) > 0 else "fallback"
    
    return routing_decision


# ============================================================
# MOJO MODULE EXPORT
# ============================================================

@export
fn PyInit_task_queue() -> PythonObject:
    """Export module for Python import."""
    let builder = PythonModuleBuilder("task_queue")
    builder.def_function[coordinate_agents]("coordinate_agents", "Determine optimal agent routing")
    return builder.build()


@export
fn PyInit_task_queue_class() -> PythonObject:
    """Export TaskQueue class for Python."""
    let builder = PythonModuleBuilder("task_queue_class")
    # TaskQueue exposed via Python wrapper
    return builder.build()
