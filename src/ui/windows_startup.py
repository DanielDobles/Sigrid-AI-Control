#!/usr/bin/env python3
"""
SIGRID Windows Startup Integration
Manages auto-start on Windows boot
"""

import sys
import os
import winreg
import shutil
from pathlib import Path
import subprocess


class WindowsStartupManager:
    """Manage SIGRID Windows startup integration."""
    
    def __init__(self):
        self.app_name = "SIGRID AI Control"
        self.app_path = self._get_app_path()
        
    def _get_app_path(self) -> str:
        """Get the path to the main application."""
        # Get the directory where this script is located
        current_dir = Path(__file__).parent.parent.parent
        main_py = current_dir / "main.py"
        desktop_app = current_dir / "src" / "ui" / "desktop_app.py"
        
        # Prefer desktop app
        if desktop_app.exists():
            return str(desktop_app)
        elif main_py.exists():
            return str(main_py)
        else:
            return str(current_dir)
    
    def enable_startup(self, minimized: bool = True) -> dict:
        """Enable SIGRID to start with Windows."""
        try:
            # Method 1: Registry (Run key)
            self._add_to_registry()
            
            # Method 2: Startup folder (backup)
            self._add_to_startup_folder()
            
            return {
                "status": "success",
                "message": "SIGRID will now start with Windows",
                "path": self.app_path
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def disable_startup(self) -> dict:
        """Disable SIGRID from starting with Windows."""
        try:
            self._remove_from_registry()
            self._remove_from_startup_folder()
            
            return {
                "status": "success",
                "message": "SIGRID will no longer start with Windows"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _add_to_registry(self):
        """Add SIGRID to Windows Run registry key."""
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            # Try current user first (no admin required)
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            python_exe = sys.executable
            command = f'"{python_exe}" "{self.app_path}"'
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
        except WindowsError:
            # Fallback to local machine (may require admin)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            python_exe = sys.executable
            command = f'"{python_exe}" "{self.app_path}"'
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
    
    def _remove_from_registry(self):
        """Remove SIGRID from Windows Run registry key."""
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
        except WindowsError:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
            except WindowsError:
                pass  # Key doesn't exist, which is fine
    
    def _get_startup_folder_path(self) -> Path:
        """Get the Windows startup folder path."""
        # User-specific startup folder
        appdata = os.getenv('APPDATA')
        if appdata:
            return Path(appdata) / r"Microsoft\Windows\Start Menu\Programs\Startup"
        return None
    
    def _add_to_startup_folder(self):
        """Create shortcut in Windows startup folder."""
        startup_folder = self._get_startup_folder_path()
        if not startup_folder:
            return
        
        startup_folder.mkdir(parents=True, exist_ok=True)
        shortcut_path = startup_folder / f"{self.app_name}.lnk"
        
        # Create a simple batch file that launches SIGRID
        batch_content = f'@echo off\n"{sys.executable}" "{self.app_path}"\n'
        batch_path = startup_folder / "SIGRID.bat"
        batch_path.write_text(batch_content)
    
    def _remove_from_startup_folder(self):
        """Remove shortcut from Windows startup folder."""
        startup_folder = self._get_startup_folder_path()
        if not startup_folder:
            return
        
        batch_path = startup_folder / "SIGRID.bat"
        if batch_path.exists():
            batch_path.unlink()
    
    def is_enabled(self) -> bool:
        """Check if SIGRID is set to start with Windows."""
        # Check registry
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            pass
        
        # Check startup folder
        startup_folder = self._get_startup_folder_path()
        if startup_folder:
            batch_path = startup_folder / "SIGRID.bat"
            if batch_path.exists():
                return True
        
        return False


def main():
    """Command-line interface for startup management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage SIGRID Windows startup")
    parser.add_argument("--enable", action="store_true", help="Enable startup")
    parser.add_argument("--disable", action="store_true", help="Disable startup")
    parser.add_argument("--status", action="store_true", help="Check status")
    
    args = parser.parse_args()
    
    manager = WindowsStartupManager()
    
    if args.enable:
        result = manager.enable_startup()
        print(f"{'✅' if result['status'] == 'success' else '❌'} {result.get('message', result.get('error'))}")
    elif args.disable:
        result = manager.disable_startup()
        print(f"{'✅' if result['status'] == 'success' else '❌'} {result.get('message', result.get('error'))}")
    elif args.status:
        enabled = manager.is_enabled()
        print(f"SIGRID startup: {'✅ Enabled' if enabled else '❌ Disabled'}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
