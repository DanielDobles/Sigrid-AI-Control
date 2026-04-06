#!/usr/bin/env python3
"""
S.I.G.R.I.D. - Self-Improving Generative Reasoning & Intelligent Decision system
Main Entry Point - AI-Powered PC Control Assistant

Powered by Google Gemma 4 + Qwen CLI + LangGraph Multi-Agent Orchestration
With Reinforcement Learning & Self-Improvement Capabilities
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.orchestrator import SIGRIDOrchestrator
from src.modules.voice import VoiceController
from src.config.settings import PROJECT_ROOT

console = Console()

def display_banner():
    """Display the SIGRID startup banner."""
    banner = Text()
    banner.append("╔══════════════════════════════════════════════════════════╗\n", style="bold cyan")
    banner.append("║                                                          ║\n", style="bold cyan")
    banner.append("║   ███████╗ █████╗ ████████╗ █████╗ ██████╗ ████████╗     ║\n", style="bold blue")
    banner.append("║   ██╔════╝██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝     ║\n", style="bold blue")
    banner.append("║   █████╗  ███████║   ██║   ███████║██████╔╝   ██║        ║\n", style="bold blue")
    banner.append("║   ██╔══╝  ██╔══██║   ██║   ██╔══██║██╔══██╗   ██║        ║\n", style="bold blue")
    banner.append("║   ██║     ██║  ██║   ██║   ██║  ██║██║  ██║   ██║        ║\n", style="bold blue")
    banner.append("║   ╚═══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ║\n", style="bold blue")
    banner.append("║                                                          ║\n", style="bold cyan")
    banner.append("║              S.I.G.R.I.D.  A I  C O N T R O L           ║\n", style="bold yellow")
    banner.append("║                                                          ║\n", style="bold cyan")
    banner.append("║  Google Gemma 4 + Qwen CLI + LangGraph + RL Learning     ║\n", style="bold green")
    banner.append("║                                                          ║\n", style="bold cyan")
    banner.append("╚══════════════════════════════════════════════════════════╝", style="bold cyan")
    
    console.print(banner)
    console.print()

def display_welcome_message(voice: VoiceController):
    """Display and speak the welcome message."""
    welcome_text = Text()
    welcome_text.append("Good day! ", style="bold bright_cyan")
    welcome_text.write(Text("I'm SIGRID, your personal AI assistant.\n\n", style="cyan"))
    welcome_text.write(Text("I'm fully operational and ready to help you with:\n", style="white"))
    welcome_text.write(Text("  📁 File System - Read, write, search, manage files\n", style="green"))
    welcome_text.write(Text("  🖱️  PC Control - Mouse, keyboard, screenshots\n", style="blue"))
    welcome_text.write(Text("  🌐 Browser - Navigate websites, extract data\n", style="magenta"))
    welcome_text.write(Text("  💻 Terminal - Execute commands\n", style="yellow"))
    welcome_text.write(Text("  🎤 Voice - Speak with me using voice commands\n\n", style="cyan"))
    welcome_text.write(Text("How can I assist you today?", style="bold bright_cyan"))
    
    console.print(Panel(
        welcome_text,
        title="[bold bright_yellow]👋 SIGRID Online[/bold bright_yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))
    console.print()
    
    # Speak welcome message
    voice.speak("Good day! I'm SIGRID, your personal AI assistant. How can I help you today?")

def cli_mode(orchestrator: SIGRIDOrchestrator, voice: VoiceController):
    """Run SIGRID in CLI mode."""
    console.print(Panel(
        "[bold white]Type your commands below. Type [red]'quit'[/red] or [red]'exit'[/red] to stop.\n"
        "Type [yellow]'help'[/yellow] for available commands.[/bold white]",
        title="[bold blue]💬 Command Interface",
        border_style="blue"
    ))
    console.print()
    
    while True:
        try:
            user_input = console.input("[bold green]You →[/bold green] ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print(Panel(
                    "[bold yellow]SIGRID shutting down. Have a great day![/bold yellow]",
                    border_style="yellow"
                ))
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            if user_input.lower() == 'voice':
                console.print("[bold cyan]🎤 Voice mode activated. Listening...[/bold cyan]")
                result = voice.listen_once(timeout=10)
                if result.get("status") == "success":
                    user_input = result["text"]
                    console.print(f"[bold magenta]📝 Recognized:[/bold magenta] {user_input}")
                else:
                    console.print("[bold red]❌ Voice recognition failed. Try again.[/bold red]")
                    continue
            
            if user_input.lower() == 'learning':
                show_learning_status(orchestrator)
                continue
            
            if user_input.lower() == 'feedback':
                provide_interactive_feedback(orchestrator)
                continue
            
            if user_input.lower() == 'improvements':
                show_improvements(orchestrator)
                continue
            
            # Process the input
            with Live(Spinner("dots", text="SIGRID is thinking...", style="cyan"), 
                     refresh_per_second=10, transient=True):
                result = orchestrator.process_input(user_input)
            
            response = result.get("ai_response", "No response generated.")
            
            # Display response
            console.print()
            console.print(Panel(
                Markdown(response),
                title="[bold cyan]🤖 SIGRID",
                border_style="cyan",
                padding=(1, 2)
            ))
            console.print()
            
            # Speak the response
            clean_response = response.split("```")[0] if "```" in response else response
            voice.speak(clean_response[:200], block=False)  # Limit speech length
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted. SIGRID standing by.[/bold yellow]")
            continue
        except Exception as e:
            console.print(Panel(
                f"[bold red]Error:[/bold red] {str(e)}",
                title="❌ Error",
                border_style="red"
            ))

def show_help():
    """Display help information."""
    help_text = """
## 📋 Available Commands

**General:**
- Type any natural language request
- SIGRID understands and executes commands

**Special Commands:**
- `help` - Show this help message
- `voice` - Switch to voice input mode
- `learning` - Show learning system status
- `feedback` - Provide feedback on last action
- `improvements` - Show self-improvement log
- `quit/exit/q` - Exit SIGRID

**Example Requests:**
- "Take a screenshot"
- "List files in my Documents folder"
- "Create a new file called test.txt with hello world"
- "Move mouse to center of screen"
- "Open google.com"
- "Search for Python files in current directory"
- "What's my screen resolution?"

**Learning Features:**
- SIGRID learns from your feedback automatically
- Use `feedback` command to rate actions
- System improves its prompts over time
- Self-improvement engine generates code fixes
"""
    console.print(Panel(
        Markdown(help_text),
        title="[bold bright_yellow]❓ Help",
        border_style="yellow",
        padding=(1, 2)
    ))


def show_learning_status(orchestrator):
    """Display the current learning system status."""
    status = orchestrator.get_learning_status()
    
    rl = status["reinforcement_learning"]
    si = status["self_improvement"]
    
    status_text = f"""
## 🧠 Learning System Status

### Reinforcement Learning
- **Total Interactions:** {rl.get('total_interactions', 0)}
- **Success Rate:** {rl.get('success_rate', 0):.1f}%
- **Successful Actions:** {rl.get('successful_actions', 0)}
- **Failed Actions:** {rl.get('failed_actions', 0)}

### Self-Improvement
- **Total Improvements:** {si.get('total_improvements', 0)}
- **Applied:** {si.get('applied', 0)}
- **Pending Review:** {si.get('pending_review', 0)}
- **Learning Rate:** {si.get('learning_rate', 0):.1f}%

### AI Engines
- **Google Gemma:** ✅ Available
- **Qwen CLI:** {'✅' if status['ai_engines']['qwen_cli']['available'] else '❌'} {status['ai_engines']['qwen_cli']['status']}
"""
    
    console.print(Panel(
        Markdown(status_text),
        title="[bold bright_cyan]📊 Learning Status",
        border_style="cyan",
        padding=(1, 2)
    ))


def provide_interactive_feedback(orchestrator):
    """Allow user to provide feedback on recent actions."""
    # Get last interaction from RL memory
    from src.learning.prompt_optimizer import PromptOptimizer
    optimizer = orchestrator.prompt_optimizer
    
    if not optimizer.rl_memory["action_history"]:
        console.print("[bold yellow]No actions to provide feedback on yet.[/bold yellow]")
        return
    
    last_action = optimizer.rl_memory["action_history"][-1]
    
    console.print(Panel(
        f"[bold white]Last Action:[/bold white]\n\n"
        f"**Type:** {last_action['action_type']}\n"
        f"**Input:** {last_action['user_input']}\n"
        f"**Result:** {last_action['action_result'].get('status', 'unknown')}\n"
        f"**ID:** {last_action['id']}",
        title="[bold yellow]💬 Feedback Request",
        border_style="yellow"
    ))
    
    success = console.input("\n[bold green]Was this action successful? (y/n):[/bold green] ").strip().lower()
    
    if success in ['y', 'yes']:
        feedback_text = console.input("[bold cyan]Additional feedback (optional):[/bold cyan] ").strip()
        result = optimizer.provide_feedback(
            interaction_id=last_action['id'],
            success=True,
            feedback_text=feedback_text
        )
        console.print(f"[bold green]✅ Feedback recorded! Reward: {result.get('reward', 0):.2f}[/bold green]")
    else:
        feedback_text = console.input("[bold red]What went wrong?[/bold red] ").strip()
        result = optimizer.provide_feedback(
            interaction_id=last_action['id'],
            success=False,
            feedback_text=feedback_text
        )
        console.print(f"[bold yellow]⚠️ Feedback recorded. SIGRID will learn from this.[/bold yellow]")


def show_improvements(orchestrator):
    """Display self-improvement log."""
    summary = orchestrator.self_improvement.get_improvement_summary()
    
    improvements_text = f"""
## 🔧 Self-Improvement Log

**Total Improvements:** {summary['total_improvements']}
**Applied:** {summary['applied']}
**Pending Review:** {summary['pending_review']}
**Learning Rate:** {summary['learning_rate']:.1f}%

### Recent Improvements:
"""
    
    for imp in summary.get("recent_improvements", []):
        improvements_text += f"\n- **{imp['id']}** ({imp['timestamp']})\n"
        improvements_text += f"  - Type: {imp.get('type', 'unknown')}\n"
        improvements_text += f"  - Status: {imp.get('status', 'unknown')}\n"
    
    console.print(Panel(
        Markdown(improvements_text),
        title="[bold bright_magenta]🔧 Improvements",
        border_style="magenta",
        padding=(1, 2)
    ))

def web_mode():
    """Launch SIGRID with web UI."""
    from src.ui.chatbot import SIGRIDChatbot

    console.print("[bold cyan]🌐 Launching web interface...[/bold cyan]")
    chatbot = SIGRIDChatbot()
    chatbot.launch()


def desktop_mode():
    """Launch SIGRID desktop application."""
    import subprocess
    
    console.print("[bold cyan]🖥️  Launching desktop application...[/bold cyan]")
    desktop_app_path = PROJECT_ROOT / "src" / "ui" / "desktop_app.py"
    
    # Start desktop app in a new process
    subprocess.Popen([sys.executable, str(desktop_app_path)])
    
    console.print("[bold green]✅ Desktop application launched![/bold green]")
    console.print("[bold yellow]Note: Closing CLI mode. Desktop app is now running.[/bold yellow]")

def main():
    """Main entry point."""
    display_banner()
    
    try:
        # Initialize voice system
        console.print("[bold cyan]🎤 Initializing voice system...[/bold cyan]")
        voice = VoiceController()
        
        # Initialize AI orchestrator
        console.print("[bold cyan]🧠 Loading AI models and agents...[/bold cyan]")
        orchestrator = SIGRIDOrchestrator()
        
        console.print("[bold green]✅ All systems operational![/bold green]\n")
        
        # Display welcome message
        display_welcome_message(voice)
        
        # Ask user which mode to use
        console.print(Panel(
            "[bold white]Choose interface mode:[/bold white]\n\n"
            "[green]1[/green]. 💻 CLI Mode (Terminal)\n"
            "[blue]2[/blue]. 🌐 Web UI (Browser)\n"
            "[magenta]3[/magenta]. 🖥️  Desktop App (Recommended)",
            title="[bold yellow]🎯 Select Mode",
            border_style="yellow"
        ))

        choice = console.input("\n[bold green]Your choice (1, 2, or 3):[/bold green] ").strip()

        if choice == '2':
            web_mode()
        elif choice == '3':
            desktop_mode()
        else:
            cli_mode(orchestrator, voice)
        
        # Cleanup
        orchestrator.cleanup()
        
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]SIGRID shutdown initiated. Goodbye![/bold yellow]")
    except Exception as e:
        console.print(Panel(
            f"[bold red]Fatal error during startup:[/bold red]\n{str(e)}\n\n"
            f"Please check your configuration and API key.",
            title="❌ Startup Failed",
            border_style="red"
        ))
        sys.exit(1)

if __name__ == "__main__":
    main()
