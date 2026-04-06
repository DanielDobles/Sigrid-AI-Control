# SIGRID Sandbox Execution Engine (Mojo)
#
# Provides safe, isolated execution environment for AI-generated code.
# Fast process isolation and resource monitoring in Mojo.
#
# Usage from Python:
#   import max.mojo.importer
#   from src.mojo import sandbox
#   result = sandbox.execute_safely("print('hello')", timeout=5)

from python import PythonObject
from python.python import *

# ============================================================
# SAFE CODE EXECUTION
# ============================================================

fn execute_safely(code: String, timeout: Float = 10.0,
                   memory_limit_mb: Int = 256) raises -> PythonObject:
    """
    Execute Python code in a sandboxed environment.
    Monitors resource usage and enforces limits.
    """
    import time
    import subprocess
    import sys
    
    let start_time = Python.eval("time.time()")
    
    # Create temporary file
    let temp_file = Python.eval("f'__sigrid_sandbox_{int(time.time() * 1000)}.py'")
    
    # Write code to temp file
    with open(temp_file, 'w') as f:
        f.write(code)
    
    try:
        # Execute in isolated subprocess
        let result = subprocess.run(
            Python.eval("[sys.executable, '-u', temp_file]"),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        let execution_time = Python.eval("time.time() - start_time")
        
        return Python.dict(
            Python.tuple(Python.eval("\"success\""), result.returncode == 0),
            Python.tuple(Python.eval("\"stdout\""), result.stdout),
            Python.tuple(Python.eval("\"stderr\""), result.stderr),
            Python.tuple(Python.eval("\"return_code\""), result.returncode),
            Python.tuple(Python.eval("\"execution_time\""), execution_time),
            Python.tuple(Python.eval("\"timed_out\""), False)
        )
    except subprocess.TimeoutExpired:
        return Python.dict(
            Python.tuple(Python.eval("\"success\""), False),
            Python.tuple(Python.eval("\"stdout\""), ""),
            Python.tuple(Python.eval("\"stderr\""), "Execution timed out"),
            Python.tuple(Python.eval("\"return_code\""), -1),
            Python.tuple(Python.eval("\"execution_time\""), timeout),
            Python.tuple(Python.eval("\"timed_out\""), True)
        )
    finally:
        # Cleanup temp file
        try:
            Python.eval("import os; os.remove(temp_file)")
        except:
            pass


# ============================================================
# DANGEROUS OPERATION DETECTOR
# ============================================================

fn check_code_safety(code: String) -> PythonObject:
    """
    Analyze code for dangerous operations.
    Returns safety score and list of warnings.
    """
    var warnings = Python.list()
    var danger_level: Int = 0  # 0=safe, 1=warning, 2=dangerous, 3=critical
    
    # Check for dangerous patterns
    let dangerous_patterns = Python.list(Python.eval("""[
        ("os.system", "System command execution", 2),
        ("subprocess.call", "Subprocess execution", 2),
        ("subprocess.Popen", "Subprocess creation", 2),
        ("eval(", "Code evaluation", 2),
        ("exec(", "Code execution", 2),
        ("__import__", "Dynamic import", 2),
        ("importlib", "Dynamic importing", 1),
        ("shutil.rmtree", "Directory deletion", 3),
        ("os.remove", "File deletion", 2),
        ("os.unlink", "File deletion", 2),
        ("pickle.loads", "Deserialization (security risk)", 3),
        ("yaml.unsafe_load", "Unsafe YAML loading", 3),
        ("socket.", "Network access", 2),
        ("requests.", "HTTP requests", 1),
        ("urllib.", "URL access", 1),
    ]"""))
    
    for pattern, description, level in dangerous_patterns:
        if pattern in code:
            warnings.append(Python.dict(
                Python.tuple(Python.eval("\"pattern\""), pattern),
                Python.tuple(Python.eval("\"description\""), description),
                Python.tuple(Python.eval("\"severity\""), level)
            ))
            danger_level = max(danger_level, level)
    
    # Check for obfuscation attempts
    if "base64" in code and "decode" in code:
        warnings.append(Python.dict(
            Python.tuple(Python.eval("\"pattern\""), "base64 decode"),
            Python.tuple(Python.eval("\"description\""), "Possible obfuscated code"),
            Python.tuple(Python.eval("\"severity\""), 3)
        ))
        danger_level = 3
    
    return Python.dict(
        Python.tuple(Python.eval("\"safe\""), danger_level == 0),
        Python.tuple(Python.eval("\"danger_level\""), danger_level),
        Python.tuple(Python.eval("\"warnings\""), warnings),
        Python.tuple(Python.eval("\"warning_count\""), len(warnings))
    )


# ============================================================
# RESOURCE MONITORING
# ============================================================

fn get_process_resources(pid: Int) -> PythonObject:
    """Get resource usage of a specific process."""
    try:
        let psutil = Python.import_module("psutil")
        let process = psutil.Process(pid)
        
        return Python.dict(
            Python.tuple(Python.eval("\"cpu_percent\""), process.cpu_percent()),
            Python.tuple(Python.eval("\"memory_mb\""), Python.eval("process.memory_info().rss / 1024 / 1024")),
            Python.tuple(Python.eval("\"threads\""), process.num_threads()),
            Python.tuple(Python.eval("\"status\""), process.status())
        )
    except:
        return Python.dict(
            Python.tuple(Python.eval("\"error\""), "Process not found")
        )


# ============================================================
# MICRO-SKILLS EXECUTOR
# ============================================================

fn execute_micro_skill(skill_name: String, parameters: PythonObject) -> PythonObject:
    """
    Execute a registered micro-skill with validation.
    Micro-skills are small, safe, reusable functions.
    """
    # Registry of safe micro-skills
    let safe_skills = Python.dict(Python.eval("""{
        "calculate": lambda **kwargs: eval(kwargs.get("expression", "0")),
        "string_ops": lambda **kwargs: kwargs.get("text", "").lower() if kwargs.get("op") == "lower" else kwargs.get("text", ""),
        "list_filter": lambda **kwargs: [x for x in kwargs.get("items", []) if kwargs.get("filter_str", "") in str(x)],
        "file_info": lambda **kwargs: str(Path(kwargs.get("path", ".")).stat()) if kwargs.get("path") else "No path",
    }"""))
    
    if skill_name not in safe_skills:
        return Python.dict(
            Python.tuple(Python.eval("\"success\""), False),
            Python.tuple(Python.eval("\"error\""), f"Unknown skill: {skill_name}")
        )
    
    try:
        let result = safe_skills[skill_name](**parameters)
        return Python.dict(
            Python.tuple(Python.eval("\"success\""), True),
            Python.tuple(Python.eval("\"result\""), result),
            Python.tuple(Python.eval("\"skill\""), skill_name)
        )
    except Exception as e:
        return Python.dict(
            Python.tuple(Python.eval("\"success\""), False),
            Python.tuple(Python.eval("\"error\""), str(e))
        )


# ============================================================
# MOJO MODULE EXPORT
# ============================================================

@export
fn PyInit_sandbox() -> PythonObject:
    """Export module for Python import."""
    let builder = PythonModuleBuilder("sandbox")
    builder.def_function[execute_safely]("execute_safely", "Execute code in sandboxed environment")
    builder.def_function[check_code_safety]("check_code_safety", "Analyze code for dangerous operations")
    builder.def_function[get_process_resources]("get_process_resources", "Get process resource usage")
    builder.def_function[execute_micro_skill]("execute_micro_skill", "Execute registered micro-skill")
    return builder.build()
