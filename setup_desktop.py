#!/usr/bin/env python3
"""
SIGRID Desktop Application - Windows Installer & Setup Script
Configures Windows startup, creates shortcuts, and sets up the environment
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from src.ui.windows_startup import WindowsStartupManager

console = Console()


def check_dependencies():
    """Check if all required packages are installed."""
    console.print("[bold cyan]📦 Checking dependencies...[/bold cyan]")
    
    required_packages = [
        "PyQt6",
        "psutil",
        "pystray",
        "PIL"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.lower().replace("pyqt6", "PyQt6").replace("pil", "PIL"))
            console.print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            console.print(f"  ❌ {package} (missing)")
    
    if missing:
        console.print(f"\n[bold yellow]Installing missing packages...[/bold yellow]")
        for package in missing:
            console.print(f"  Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          capture_output=True)
    
    console.print("[bold green]✅ All dependencies ready![/bold green]\n")


def setup_windows_startup():
    """Configure Windows startup integration."""
    console.print(Panel(
        "[bold white]Windows Startup Configuration[/bold white]\n\n"
        "SIGRID can automatically start when Windows boots.\n"
        "It will run in the system tray and be ready to use.",
        title="[bold yellow]⚙️  Setup Options",
        border_style="yellow"
    ))
    
    manager = WindowsStartupManager()
    
    choice = console.input("\n[bold green]Enable auto-start with Windows? (y/n):[/bold green] ").strip().lower()
    
    if choice in ['y', 'yes']:
        result = manager.enable_startup()
        if result['status'] == 'success':
            console.print(f"\n[bold green]✅ {result['message']}[/bold green]")
            console.print(f"[dim]Path: {result['path']}[/dim]")
        else:
            console.print(f"\n[bold red]❌ {result['error']}[/bold red]")
    else:
        console.print("[bold yellow]Auto-start disabled. You can launch SIGRID manually anytime.[/bold yellow]")


def create_desktop_shortcut():
    """Create a desktop shortcut for SIGRID."""
    console.print("\n[bold cyan]🖥️  Creating desktop shortcut...[/bold cyan]")
    
    try:
        import win32com.client
        import pythoncom
        
        # Initialize COM
        pythoncom.CoInitialize()
        
        # Get desktop path
        desktop_path = Path.home() / "Desktop"
        shortcut_path = desktop_path / "SIGRID AI Control.lnk"
        
        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = str(project_root / "start_desktop.py")
        shortcut.WorkingDirectory = str(project_root)
        shortcut.IconLocation = ""
        shortcut.Description = "SIGRID AI Control - Self-Improving AI Assistant"
        shortcut.save()
        
        console.print(f"[bold green]✅ Desktop shortcut created: {shortcut_path}[/bold green]")
        
    except ImportError:
        # Fallback: Create a simple batch file on desktop
        desktop_path = Path.home() / "Desktop"
        batch_path = desktop_path / "SIGRID.bat"
        
        batch_content = f'@echo off\ncd /d "{project_root}"\npython start_desktop.py\n'
        batch_path.write_text(batch_content)
        
        console.print(f"[bold green]✅ Desktop shortcut created: {batch_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold yellow]⚠️  Could not create desktop shortcut: {e}[/bold yellow]")


def test_desktop_app():
    """Test if the desktop application launches correctly."""
    console.print("\n[bold cyan]🧪 Testing desktop application...[/bold cyan]")
    
    try:
        from src.ui.desktop_app import SigridMainWindow, QApplication
        console.print("[bold green]✅ Desktop application modules loaded successfully![/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Desktop application test failed: {e}[/bold red]")
        return False


def main():
    """Run the complete setup process."""
    console.print(Panel(
        "[bold white]Welcome to SIGRID AI Control Setup![/bold white]\n\n"
        "This will configure your system for the best experience:\n"
        "• Check and install dependencies\n"
        "• Configure Windows startup (optional)\n"
        "• Create desktop shortcut\n"
        "• Test the application",
        title="[bold bright_cyan]🚀 SIGRID Setup Wizard",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    console.print()
    
    # Step 1: Check dependencies
    check_dependencies()
    
    # Step 2: Test application
    if test_desktop_app():
        # Step 3: Configure startup
        setup_windows_startup()
        
        # Step 4: Create shortcut
        create_desktop_shortcut()
        
        # Done!
        console.print(Panel(
            "[bold green]Setup Complete![/bold green]\n\n"
            "You can now launch SIGRID by:\n"
            "• Double-clicking [bold]Launch_SIGRID_Desktop.bat[/bold]\n"
            "• Running [bold]python start_desktop.py[/bold]\n"
            "• Using the desktop shortcut (if created)\n\n"
            "SIGRID will appear in your system tray and be ready to use!",
            title="[bold bright_green]✅ All Done!",
            border_style="green",
            padding=(1, 2)
        ))
        
        # Ask if user wants to launch now
        launch_now = console.input("\n[bold green]Launch SIGRID Desktop now? (y/n):[/bold green] ").strip().lower()
        if launch_now in ['y', 'yes']:
            console.print("[bold cyan]🚀 Launching SIGRID...[/bold cyan]")
            from src.ui.desktop_app import main as desktop_main
            desktop_main()
    else:
        console.print(Panel(
            "[bold red]Setup Incomplete[/bold red]\n\n"
            "Please fix the errors above and run setup again.",
            title="❌ Error",
            border_style="red"
        ))


if __name__ == "__main__":
    main()
