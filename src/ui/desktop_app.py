#!/usr/bin/env python3
"""
SIGRID Desktop Application
Professional Desktop GUI with Chat, Resource Monitor, and System Tray
"""

import sys
import os
import json
import psutil
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QGroupBox, QLabel, QProgressBar,
    QSplitter, QTabWidget, QSystemTrayIcon, QMenu, QMessageBox,
    QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QFont, QIcon, QColor, QTextCursor, QPalette, QPixmap,
    QAction, QKeySequence
)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.orchestrator import SigridOrchestrator
from src.mojo import mojo  # Mojo integration


# ============================================================
# RESOURCE MONITOR THREAD
# ============================================================
class ResourceMonitorThread(QThread):
    """Background thread that monitors PC resources."""
    resources_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_freq = psutil.cpu_freq()
                cpu_freq_current = cpu_freq.current if cpu_freq else 0
                cpu_freq_max = cpu_freq.max if cpu_freq else 0
                
                # Memory
                memory = psutil.virtual_memory()
                
                # Disk
                disk = psutil.disk_usage('C:\\')
                
                # Network
                net_io = psutil.net_io_counters()
                
                # GPU (if available via NVIDIA)
                gpu_info = self._get_gpu_info()
                
                # Top processes
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        pinfo = proc.info
                        if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 0:
                            processes.append({
                                'pid': pinfo['pid'],
                                'name': pinfo['name'],
                                'cpu': pinfo['cpu_percent'],
                                'memory': pinfo['memory_percent']
                            })
                    except:
                        pass
                processes.sort(key=lambda x: x['cpu'], reverse=True)
                top_processes = processes[:5]
                
                data = {
                    'cpu': {
                        'percent': cpu_percent,
                        'freq_current': cpu_freq_current,
                        'freq_max': cpu_freq_max,
                        'cores': psutil.cpu_count(logical=False),
                        'threads': psutil.cpu_count(logical=True)
                    },
                    'memory': {
                        'percent': memory.percent,
                        'used_gb': memory.used / (1024**3),
                        'total_gb': memory.total / (1024**3),
                        'available_gb': memory.available / (1024**3)
                    },
                    'disk': {
                        'percent': disk.percent,
                        'used_gb': disk.used / (1024**3),
                        'total_gb': disk.total / (1024**3),
                        'free_gb': disk.free / (1024**3)
                    },
                    'network': {
                        'bytes_sent_mb': net_io.bytes_sent / (1024**2),
                        'bytes_recv_mb': net_io.bytes_recv / (1024**2)
                    },
                    'gpu': gpu_info,
                    'top_processes': top_processes,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                
                self.resources_updated.emit(data)
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                self.error_occurred.emit(str(e))
                time.sleep(5)
    
    def _get_gpu_info(self) -> dict:
        """Get GPU information if available."""
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.used,memory.total,utilization.gpu', 
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpus = []
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) == 4:
                        gpus.append({
                            'name': parts[0],
                            'memory_used': parts[1],
                            'memory_total': parts[2],
                            'utilization': parts[3]
                        })
                return {'available': True, 'gpus': gpus}
        except:
            pass
        return {'available': False, 'gpus': []}
    
    def stop(self):
        self.running = False


# ============================================================
# AI WORKER THREAD
# ============================================================
class AIWorkerThread(QThread):
    """Background thread for processing AI requests."""
    response_ready = pyqtSignal(str, str)  # user_message, ai_response
    error_occurred = pyqtSignal(str, str)  # user_message, error
    typing_started = pyqtSignal()
    typing_finished = pyqtSignal()
    
    def __init__(self, orchestrator: SigridOrchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self.message_queue = []
        self.lock = threading.Lock()
        self.running = True
        
    def run(self):
        while self.running:
            if self.message_queue:
                with self.lock:
                    user_message, conversation_id = self.message_queue.pop(0)
                
                try:
                    self.typing_started.emit()
                    result = self.orchestrator.process_input(user_message, thread_id=conversation_id)
                    response = result.get('ai_response', 'No response generated.')
                    self.typing_finished.emit()
                    self.response_ready.emit(user_message, response)
                except Exception as e:
                    self.typing_finished.emit()
                    self.error_occurred.emit(user_message, str(e))
            else:
                time.sleep(0.1)
    
    def add_message(self, message: str, conversation_id: str = "default"):
        with self.lock:
            self.message_queue.append((message, conversation_id))
    
    def stop(self):
        self.running = False


# ============================================================
# CHAT WIDGET
# ============================================================
class ChatWidget(QWidget):
    """Modern chat interface widget."""
    
    message_sent = pyqtSignal(str)  # Signal emitted when user sends a message
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Chat messages area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: none;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
            QTextEdit:focus {
                outline: none;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message to SIGRID...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #89b4fa;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Typing indicator
        self.typing_label = QLabel("SIGRID is typing...")
        self.typing_label.setStyleSheet("""
            QLabel {
                color: #89b4fa;
                font-size: 12px;
                padding: 5px 15px;
                font-style: italic;
            }
        """)
        self.typing_label.hide()
        layout.addWidget(self.typing_label)
        
    def add_message(self, sender: str, message: str, is_error: bool = False):
        """Add a message to the chat."""
        timestamp = datetime.now().strftime('%H:%M')
        
        # Sender header
        if sender == "You":
            sender_color = "#a6e3a1"
            bg_color = "#313244"
        else:
            sender_color = "#89b4fa"
            bg_color = "#45475a"
        
        if is_error:
            sender_color = "#f38ba8"
            bg_color = "#45475a"
        
        html = f"""
        <div style="margin: 10px 0;">
            <div style="color: {sender_color}; font-weight: bold; font-size: 12px;">
                {sender} • {timestamp}
            </div>
            <div style="background-color: {bg_color}; padding: 12px; border-radius: 10px; margin-top: 5px;">
                {message}
            </div>
        </div>
        """
        
        self.chat_area.append(html)
        self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
        
    def show_typing(self):
        self.typing_label.show()
        
    def hide_typing(self):
        self.typing_label.hide()
        
    def clear_chat(self):
        self.chat_area.clear()
        
    def send_message(self):
        """Emit the message_sent signal with user input."""
        message = self.input_field.text().strip()
        if message:
            self.message_sent.emit(message)
            self.input_field.clear()


# ============================================================
# RESOURCE MONITOR WIDGET
# ============================================================
class ResourceMonitorWidget(QWidget):
    """Real-time PC resource monitor."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # CPU Group
        cpu_group, self.cpu_bar, self.cpu_label = self._create_progress_group("CPU", "#89b4fa")
        layout.addWidget(cpu_group)
        
        # Memory Group
        mem_group, self.mem_bar, self.mem_label = self._create_progress_group("Memory", "#a6e3a1")
        layout.addWidget(mem_group)
        
        # Disk Group
        disk_group, self.disk_bar, self.disk_label = self._create_progress_group("Disk C:", "#f9e2af")
        layout.addWidget(disk_group)
        
        # GPU Group (optional)
        gpu_group, self.gpu_bar, self.gpu_label = self._create_progress_group("GPU", "#cba6f7")
        layout.addWidget(gpu_group)
        
        # Network
        net_group, _, self.net_label = self._create_progress_group("Network", "#94e2d5")
        layout.addWidget(net_group)
        
        # Top Processes
        processes_group = QGroupBox("Top Processes")
        processes_group.setStyleSheet("""
            QGroupBox {
                color: #cdd6f4;
                font-size: 13px;
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        processes_layout = QVBoxLayout()
        self.processes_label = QLabel("No processes data")
        self.processes_label.setStyleSheet("color: #a6adc8; font-size: 12px;")
        processes_layout.addWidget(self.processes_label)
        processes_group.setLayout(processes_layout)
        layout.addWidget(processes_group)
        
        layout.addStretch()
        
    def _create_progress_group(self, title: str, color: str) -> tuple:
        """Create a group with progress bar. Returns (group, bar, label)."""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                color: #cdd6f4;
                font-size: 13px;
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {color};
            }}
        """)
        
        layout = QVBoxLayout()
        label = QLabel("Loading...")
        label.setObjectName(f"{title.lower().replace(' ', '_')}_label")
        label.setStyleSheet(f"color: {color}; font-size: 12px;")
        layout.addWidget(label)
        
        bar = QProgressBar()
        bar.setObjectName(f"{title.lower().replace(' ', '_')}_bar")
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #313244;
                border: none;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                color: #1e1e2e;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        bar.setMaximum(100)
        bar.setValue(0)
        layout.addWidget(bar)
        
        group.setLayout(layout)
        return group, bar, label
        
    def update_resources(self, data: dict):
        """Update resource display with new data."""
        # CPU
        cpu = data['cpu']
        self.cpu_bar.setValue(int(cpu['percent']))
        self.cpu_label.setText(
            f"{cpu['percent']:.1f}% | "
            f"{cpu['cores']} cores / {cpu['threads']} threads | "
            f"{cpu['freq_current']:.0f} MHz"
        )
        
        # Memory
        mem = data['memory']
        self.mem_bar.setValue(int(mem['percent']))
        self.mem_label.setText(
            f"{mem['percent']:.1f}% | "
            f"{mem['used_gb']:.1f} GB / {mem['total_gb']:.1f} GB | "
            f"{mem['available_gb']:.1f} GB available"
        )
        
        # Disk
        disk = data['disk']
        self.disk_bar.setValue(int(disk['percent']))
        self.disk_label.setText(
            f"{disk['percent']:.1f}% | "
            f"{disk['used_gb']:.1f} GB / {disk['total_gb']:.1f} GB | "
            f"{disk['free_gb']:.1f} GB free"
        )
        
        # GPU
        gpu = data['gpu']
        if gpu['available'] and gpu['gpus']:
            gpu_data = gpu['gpus'][0]
            self.gpu_label.setText(f"{gpu_data['name']}")
            self.gpu_bar.setValue(int(float(gpu_data['utilization'])))
        else:
            self.gpu_label.setText("No GPU detected")
            self.gpu_bar.setValue(0)
        
        # Network
        net = data['network']
        self.net_label.setText(
            f"↑ {net['bytes_sent_mb']:.1f} MB sent | "
            f"↓ {net['bytes_recv_mb']:.1f} MB received"
        )
        
        # Processes
        processes = data['top_processes']
        if processes:
            proc_text = "\n".join([
                f"• {p['name']} (PID: {p['pid']}) - CPU: {p['cpu']:.1f}% | Mem: {p['memory']:.1f}%"
                for p in processes
            ])
            self.processes_label.setText(proc_text)
        else:
            self.processes_label.setText("No active processes")


# ============================================================
# ERROR LOG WIDGET
# ============================================================
class ErrorLogWidget(QWidget):
    """Display and manage system errors."""
    
    def __init__(self):
        super().__init__()
        self.errors = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Error display
        self.error_display = QTextEdit()
        self.error_display.setReadOnly(True)
        self.error_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                color: #f38ba8;
                border: none;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.error_display)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear Errors")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        clear_btn.clicked.connect(self.clear_errors)
        layout.addWidget(clear_btn)
        
    def add_error(self, error_type: str, error_message: str, context: str = ""):
        """Add an error to the log."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.errors.append({
            'timestamp': timestamp,
            'type': error_type,
            'message': error_message,
            'context': context
        })
        
        error_html = f"""
        <div style="margin: 8px 0; padding: 8px; background-color: #313244; border-radius: 5px; border-left: 3px solid #f38ba8;">
            <div style="color: #f38ba8; font-weight: bold;">[{timestamp}] {error_type}</div>
            <div style="color: #a6adc8; margin-top: 4px;">{error_message}</div>
            {f'<div style="color: #6c7086; margin-top: 4px; font-size: 11px;">{context}</div>' if context else ''}
        </div>
        """
        self.error_display.append(error_html)
        self.error_display.moveCursor(QTextCursor.MoveOperation.End)
        
    def clear_errors(self):
        self.errors.clear()
        self.error_display.clear()


# ============================================================
# MAIN WINDOW
# ============================================================
class SigridMainWindow(QMainWindow):
    """Main SIGRID desktop application window."""
    
    def __init__(self):
        super().__init__()
        self.orchestrator = None
        self.ai_worker = None
        self.resource_monitor = None
        self.init_ui()
        self.init_system_tray()
        self.start_background_threads()
        
    def init_ui(self):
        """Initialize the main window UI."""
        self.setWindowTitle("SIGRID AI Control - Self-Improving AI Assistant")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left panel - Chat
        left_panel = QVBoxLayout()
        left_panel.setSpacing(0)
        
        # Header
        header_label = QLabel("💬 SIGRID Chat")
        header_label.setStyleSheet("""
            QLabel {
                color: #89b4fa;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        left_panel.addWidget(header_label)
        
        # Chat widget
        self.chat_widget = ChatWidget()
        self.chat_widget.message_sent.connect(self.handle_user_message)
        left_panel.addWidget(self.chat_widget)
        
        # Right panel - Tabs
        right_panel = QTabWidget()
        right_panel.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #45475a;
                background-color: #1e1e2e;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #cdd6f4;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #45475a;
            }
            QTabBar::tab:hover {
                background-color: #585b70;
            }
        """)
        
        # Resource monitor tab
        self.resource_widget = ResourceMonitorWidget()
        right_panel.addTab(self.resource_widget, "📊 Resources")
        
        # Error log tab
        self.error_widget = ErrorLogWidget()
        right_panel.addTab(self.error_widget, "⚠️ Errors")
        
        # Learning status tab
        self.learning_widget = self._create_learning_widget()
        right_panel.addTab(self.learning_widget, "🧠 Learning")
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("SIGRID Initializing...", 0)
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #313244;
                color: #cdd6f4;
                font-size: 12px;
            }
        """)
        
    def _create_learning_widget(self) -> QWidget:
        """Create the learning status display widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.learning_status_label = QLabel("Learning system initializing...")
        self.learning_status_label.setStyleSheet("""
            QLabel {
                color: #cdd6f4;
                font-size: 14px;
                padding: 15px;
                background-color: #313244;
                border-radius: 8px;
            }
        """)
        self.learning_status_label.setWordWrap(True)
        layout.addWidget(self.learning_status_label)
        
        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_learning_status)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        return widget
        
    def init_system_tray(self):
        """Initialize system tray icon and menu."""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        # Use a simple icon (will show in system tray)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        self.tray_icon.setToolTip("SIGRID AI Control")
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show SIGRID", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # Quick actions
        screenshot_action = QAction("📸 Take Screenshot", self)
        screenshot_action.triggered.connect(lambda: self.quick_command("Take a screenshot"))
        tray_menu.addAction(screenshot_action)
        
        files_action = QAction("📁 List Documents", self)
        files_action.triggered.connect(lambda: self.quick_command("List files in my Documents folder"))
        tray_menu.addAction(files_action)
        
        tray_menu.addSeparator()
        
        minimize_action = QAction("Minimize to Tray", self)
        minimize_action.triggered.connect(self.hide)
        tray_menu.addAction(minimize_action)
        
        quit_action = QAction("Quit SIGRID", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Tray icon double-click
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
            
    def quick_command(self, command: str):
        """Execute a quick command from tray menu."""
        self.show()
        self.activateWindow()
        self.chat_widget.input_field.setText(command)
        self.chat_widget.send_message()
        
    def start_background_threads(self):
        """Start all background threads."""
        try:
            # Initialize orchestrator
            self.statusBar().showMessage("Initializing AI orchestrator...")
            self.orchestrator = SigridOrchestrator()
            
            # Start AI worker
            self.ai_worker = AIWorkerThread(self.orchestrator)
            self.ai_worker.response_ready.connect(self.on_ai_response)
            self.ai_worker.error_occurred.connect(self.on_ai_error)
            self.ai_worker.typing_started.connect(self.chat_widget.show_typing)
            self.ai_worker.typing_finished.connect(self.chat_widget.hide_typing)
            self.ai_worker.start()
            
            # Start resource monitor
            self.resource_monitor = ResourceMonitorThread()
            self.resource_monitor.resources_updated.connect(self.resource_widget.update_resources)
            self.resource_monitor.error_occurred.connect(self.on_resource_error)
            self.resource_monitor.start()
            
            # Welcome message
            self.chat_widget.add_message("SIGRID", 
                "👋 Good day! I'm <b>SIGRID</b>, your personal AI assistant with self-learning capabilities.<br><br>"
                "I can help you with:<br>"
                "• 📁 <b>File System</b> - Read, write, search, manage files<br>"
                "• 🖱️ <b>PC Control</b> - Mouse, keyboard, screenshots<br>"
                "• 🌐 <b>Browser</b> - Navigate websites, extract data<br>"
                "• 💻 <b>Terminal</b> - Execute commands<br>"
                "• 🎤 <b>Voice</b> - Use the voice button to speak<br><br>"
                "I <b>learn</b> from your feedback and <b>improve</b> myself automatically!<br><br>"
                "How can I assist you today?"
            )
            
            self.statusBar().showMessage("✅ SIGRID Ready")
            
        except Exception as e:
            self.error_widget.add_error("Startup Error", str(e))
            QMessageBox.critical(self, "Startup Error", 
                f"Failed to initialize SIGRID:\n\n{str(e)}\n\n"
                f"Please check your API key in .env file.")
            
    def handle_user_message(self, message: str):
        """Handle message from chat widget signal."""
        self.chat_widget.add_message("You", message)
        
        # Send to AI worker
        self.ai_worker.add_message(message)
        
    def on_ai_response(self, user_message: str, ai_response: str):
        """Handle AI response."""
        self.chat_widget.add_message("SIGRID", ai_response)
        self.statusBar().showMessage(f"✅ Responded at {datetime.now().strftime('%H:%M:%S')}")
        
        # Update learning status if available
        try:
            self.refresh_learning_status()
        except:
            pass
            
    def on_ai_error(self, user_message: str, error: str):
        """Handle AI error."""
        self.chat_widget.add_message("SIGRID", 
            f"⚠️ I encountered an error processing your request:<br><br>"
            f"<code style='color: #f38ba8;'>{error}</code><br><br>"
            f"Please try again or check the error log for details.",
            is_error=True
        )
        self.error_widget.add_error("AI Processing Error", error, f"Request: {user_message}")
        self.statusBar().showMessage("❌ Error processing request")
        
    def on_resource_error(self, error: str):
        """Handle resource monitoring error."""
        self.error_widget.add_error("Resource Monitor", error)
        
    def refresh_learning_status(self):
        """Refresh the learning status display."""
        if not self.orchestrator:
            return
            
        try:
            status = self.orchestrator.get_learning_status()
            rl = status['reinforcement_learning']
            si = status['self_improvement']
            
            # Add Mojo status
            status['mojo'] = mojo.get_status()
            
            html = f"""
            <h3 style="color: #89b4fa;">🧠 Learning System Status</h3>
            
            <h4 style="color: #a6e3a1;">Reinforcement Learning</h4>
            <ul>
                <li><b>Total Interactions:</b> {rl.get('total_interactions', 0)}</li>
                <li><b>Success Rate:</b> {rl.get('success_rate', 0):.1f}%</li>
                <li><b>Successful Actions:</b> {rl.get('successful_actions', 0)}</li>
                <li><b>Failed Actions:</b> {rl.get('failed_actions', 0)}</li>
            </ul>
            
            <h4 style="color: #f9e2af;">Self-Improvement</h4>
            <ul>
                <li><b>Total Improvements:</b> {si.get('total_improvements', 0)}</li>
                <li><b>Applied:</b> {si.get('applied', 0)}</li>
                <li><b>Pending Review:</b> {si.get('pending_review', 0)}</li>
                <li><b>Learning Rate:</b> {si.get('learning_rate', 0):.1f}%</li>
            </ul>
            
            <h4 style="color: #cba6f7;">AI Engines</h4>
            <ul>
                <li><b>Google Gemma:</b> ✅ Available</li>
                <li><b>Qwen CLI:</b> {'✅' if status['ai_engines']['qwen_cli']['available'] else '❌'} {status['ai_engines']['qwen_cli']['status']}</li>
            </ul>
            
            <h4 style="color: #f38ba8;">Performance Layer (Mojo)</h4>
            <ul>
                <li><b>Mojo Runtime:</b> {'✅ Available (Native Speed)' if status['mojo']['mojo_available'] else '⚠️ Python Fallback'}</li>
                <li><b>Image Processing:</b> {status['mojo']['image_processor']}</li>
                <li><b>Task Queue:</b> {status['mojo']['task_queue']}</li>
                <li><b>Sandbox:</b> {status['mojo']['sandbox']}</li>
            </ul>
            """
            
            self.learning_status_label.setText(html)
        except Exception as e:
            self.learning_status_label.setText(f"Error loading learning status: {e}")
            
    def closeEvent(self, event):
        """Handle window close event."""
        event.ignore()  # Don't actually close
        self.hide()  # Minimize to tray instead
        self.tray_icon.showMessage(
            "SIGRID Minimized",
            "SIGRID is still running in the system tray. Double-click to restore.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
        
    def quit_application(self):
        """Properly quit the application."""
        # Stop background threads
        if self.ai_worker:
            self.ai_worker.stop()
            self.ai_worker.wait(3000)
            
        if self.resource_monitor:
            self.resource_monitor.stop()
            self.resource_monitor.wait(3000)
            
        if self.orchestrator:
            self.orchestrator.cleanup()
            
        QApplication.quit()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================
def main():
    """Main application entry point."""
    # Fix Windows DPI awareness
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per Monitor DPI Aware
    except:
        pass  # Skip if not on Windows or fails
    
    app = QApplication(sys.argv)
    app.setApplicationName("SIGRID AI Control")
    app.setOrganizationName("SIGRID")
    app.setApplicationVersion("1.0.0")
    
    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#313244"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#45475a"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1e1e2e"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#45475a"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#cdd6f4"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#f38ba8"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#89b4fa"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#89b4fa"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1e1e2e"))
    app.setPalette(palette)
    
    # Create and show main window
    window = SigridMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
