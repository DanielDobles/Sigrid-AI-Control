# 🖥️ SIGRID Desktop Application Guide

Professional desktop GUI with system tray, resource monitoring, and Windows integration.

## 🎯 Quick Start

### Option 1: Double-Click Launcher (Easiest)
Simply double-click: **`Launch_SIGRID_Desktop.bat`**

### Option 2: Python Script
```bash
cd C:\Users\armon\DEV\Sigrid-AI-Control
python start_desktop.py
```

### Option 3: Full Setup (Recommended First Time)
```bash
cd C:\Users\armon\DEV\Sigrid-AI-Control
python setup_desktop.py
```

This will:
- ✅ Check and install all dependencies
- ✅ Configure Windows auto-start (optional)
- ✅ Create desktop shortcut
- ✅ Test the application
- ✅ Launch SIGRID

---

## 🖥️ Desktop Application Features

### 1. **Modern Chat Interface**
- Beautiful dark theme (Catppuccin Mocha)
- Real-time message display with timestamps
- Typing indicator ("SIGRID is typing...")
- Message history with color-coded senders
- Error highlighting in red
- Smooth scrolling and auto-scroll to latest message

### 2. **Real-Time Resource Monitor**
Live monitoring of your PC's resources:

#### CPU Monitor
- Current usage percentage
- Core and thread count
- Clock speed (MHz)
- Color-coded progress bar

#### Memory (RAM) Monitor
- Usage percentage
- Used / Total GB
- Available memory
- Real-time updates (every 2 seconds)

#### Disk Monitor
- C: drive usage
- Used / Total / Free space
- Percentage indicator

#### GPU Monitor
- NVIDIA GPU detection (if available)
- GPU name
- Memory usage
- Utilization percentage

#### Network Monitor
- Upload/download in MB
- Real-time traffic stats

#### Top Processes
- Shows top 5 CPU-consuming processes
- PID, name, CPU%, Memory%
- Auto-sorted by usage

### 3. **System Tray Integration**
SIGRID runs in your Windows system tray:

**Tray Icon Menu:**
- 📸 **Take Screenshot** - Quick screenshot command
- 📁 **List Documents** - Quick file browser
- **Minimize to Tray** - Hide window (app keeps running)
- **Quit SIGRID** - Properly shutdown

**Tray Interactions:**
- **Double-click** icon → Restore window
- **Right-click** → Open menu
- **Notifications** → Shows when minimized

**Close Button Behavior:**
- Clicking ❌ **does NOT quit** the app
- It minimizes to system tray instead
- SIGRID keeps running in background
- Use tray menu → "Quit SIGRID" to actually exit

### 4. **Error Management System**
Dedicated error logging tab:

**Features:**
- Timestamped error entries
- Error type classification
- Detailed error messages
- Context information (what caused the error)
- One-click error clearing
- Color-coded severity

**Error Sources Tracked:**
- AI processing errors
- Resource monitor errors
- Startup failures
- Network issues
- File system errors

### 5. **Learning Status Dashboard**
View SIGRID's learning progress:

**Reinforcement Learning Stats:**
- Total interactions
- Success rate %
- Successful vs failed actions

**Self-Improvement Stats:**
- Total improvements generated
- Applied vs pending review
- Learning rate %

**AI Engine Status:**
- Google Gemma availability
- Qwen CLI availability

---

## 🪟 Windows Startup Integration

### What It Does
When enabled, SIGRID will:
1. **Auto-start** when Windows boots
2. **Run in system tray** (minimized by default)
3. **Be ready to use** without manual launch
4. **Use minimal resources** when idle

### How It Works
SIGRID uses two methods for maximum compatibility:

**Method 1: Windows Registry**
```
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
→ "SIGRID AI Control" = "C:\Python\python.exe" "C:\...\desktop_app.py"
```

**Method 2: Startup Folder**
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
→ SIGRID.bat (launches the desktop app)
```

### Enable/Disable Startup

**Via Setup Script:**
```bash
python setup_desktop.py
# Choose "y" when asked about auto-start
```

**Via Command Line:**
```bash
# Enable
python src/ui/windows_startup.py --enable

# Disable
python src/ui/windows_startup.py --disable

# Check status
python src/ui/windows_startup.py --status
```

**Programmatically:**
```python
from src.ui.windows_startup import WindowsStartupManager

manager = WindowsStartupManager()

# Enable
result = manager.enable_startup()
print(result['message'])

# Disable
result = manager.disable_startup()
print(result['message'])

# Check if enabled
if manager.is_enabled():
    print("SIGRID starts with Windows")
```

---

## 🎨 User Interface Tour

### Main Window Layout

```
┌──────────────────────────────────────────────────────────┐
│  SIGRID AI Control - Self-Improving AI Assistant     [─][□][×]│
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────┐  ┌─────────────────────────────┐│
│  │  💬 SIGRID Chat    │  │ [📊 Resources] [⚠️ Errors]  ││
│  │                    │  │ [🧠 Learning]               ││
│  │  Messages area     │  │                             ││
│  │  (scrollable)      │  │  Tab content area           ││
│  │                    │  │                             ││
│  │  ┌──────────────┐  │  │  • CPU: 45%                 ││
│  │  │ Type here... │  │  │  • RAM: 62%                 ││
│  │  └──────────────┘  │  │  • Disk: 78%                ││
│  │  [Send]            │  │  • Network: ↑↓              ││
│  │                    │  │  • Top processes            ││
│  └────────────────────┘  └─────────────────────────────┘│
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ✅ SIGRID Ready                            [System Tray]│
└──────────────────────────────────────────────────────────┘
```

### Color Scheme (Catppuccin Mocha)

| Element | Color | Hex |
|---------|-------|-----|
| Background | Base | `#1e1e2e` |
| Input fields | Surface0 | `#313244` |
| Borders | Overlay0 | `#45475a` |
| Text | Text | `#cdd6f4` |
| User messages | Green | `#a6e3a1` |
| SIGRID messages | Blue | `#89b4fa` |
| Errors | Red | `#f38ba8` |
| Warnings | Yellow | `#f9e2af` |
| GPU | Mauve | `#cba6f7` |
| Network | Teal | `#94e2d5` |

---

## 💡 Usage Examples

### Basic Chat
1. Type in the input field: `Take a screenshot`
2. Press Enter or click "Send"
3. See "SIGRID is typing..." indicator
4. Response appears in chat area

### Monitor Resources
1. Click "📊 Resources" tab
2. Watch real-time updates every 2 seconds
3. See which processes use most CPU
4. Monitor disk space and network traffic

### Check Errors
1. Click "⚠️ Errors" tab
2. View all system errors chronologically
3. See error details and context
4. Click "🗑️ Clear Errors" to reset

### View Learning Progress
1. Click "🧠 Learning" tab
2. Click "🔄 Refresh Status"
3. See SIGRID's improvement statistics

### System Tray Actions
1. Right-click tray icon
2. Select "📸 Take Screenshot"
3. SIGRID executes command immediately
4. Window appears with result

### Minimize to Tray
1. Click window ❌ button
2. Window disappears
3. SIGRID still running in tray
4. Double-click tray icon to restore

---

## 🔧 Configuration

### Window Size
Edit in `src/ui/desktop_app.py`:
```python
# Line in init_ui()
self.setGeometry(100, 100, 1400, 900)  # x, y, width, height
self.setMinimumSize(1000, 700)  # minimum width, height
```

### Resource Monitor Update Interval
```python
# In ResourceMonitorThread.run()
time.sleep(2)  # Change to update faster/slower
```

### Chat Appearance
```python
# In ChatWidget.init_ui()
self.chat_area.setStyleSheet("""
    QTextEdit {
        font-size: 14px;  /* Change text size */
        line-height: 1.6; /* Change spacing */
    }
""")
```

### System Tray Icon
```python
# In init_system_tray()
self.tray_icon.setIcon(
    self.style().standardIcon(
        self.style().StandardPixmap.SP_ComputerIcon
    )
)
# Replace with custom icon:
# self.tray_icon.setIcon(QIcon("path/to/icon.png"))
```

---

## 🐛 Troubleshooting

### "Failed to initialize SIGRID"
**Cause:** API key missing or invalid
**Fix:** Check `.env` file has correct `GOOGLE_API_KEY`

### Desktop app won't launch
**Cause:** Missing PyQt6
**Fix:** `pip install PyQt6 psutil pystray`

### Resource monitor shows 0%
**Cause:** psutil not installed
**Fix:** `pip install psutil`

### System tray icon missing
**Cause:** Windows Explorer glitch
**Fix:** Restart Windows Explorer or reboot

### Auto-start not working
**Cause:** Registry permissions
**Fix:** Run setup as administrator

### Window closes instead of minimizing
**Cause:** Bug in closeEvent
**Fix:** Check `closeEvent()` method in code

---

## 📊 Performance

### Resource Usage
- **Idle (tray only):** ~150 MB RAM, <1% CPU
- **Active chat:** ~200 MB RAM, 2-5% CPU
- **Processing request:** ~250 MB RAM, 10-20% CPU
- **Resource monitor:** Adds ~2% CPU overhead

### Startup Time
- **Cold start:** 3-5 seconds
- **Warm start:** 1-2 seconds
- **AI initialization:** Runs in background

---

## 🚀 Advanced Features

### Quick Commands from Tray
Add more quick actions:
```python
# In init_system_tray()
custom_action = QAction("🎯 Custom Command", self)
custom_action.triggered.connect(
    lambda: self.quick_command("your command here")
)
tray_menu.addAction(custom_action)
```

### Custom Resource Alerts
Add threshold alerts:
```python
# In update_resources()
if data['cpu']['percent'] > 90:
    self.tray_icon.showMessage(
        "⚠️ High CPU Usage",
        f"CPU at {data['cpu']['percent']}%",
        QSystemTrayIcon.MessageIcon.Warning,
        3000
    )
```

### Voice Integration
Add voice button to chat:
```python
# In ChatWidget.init_ui()
voice_btn = QPushButton("🎤")
voice_btn.clicked.connect(self.start_voice_input)
input_layout.addWidget(voice_btn)
```

---

## 📝 File Structure

```
Sigrid-AI-Control/
├── main.py                      # Main launcher (3 modes)
├── start_desktop.py             # Quick desktop launcher
├── setup_desktop.py             # Full setup wizard
├── Launch_SIGRID_Desktop.bat    # Windows batch launcher
│
├── src/
│   └── ui/
│       ├── desktop_app.py       # Main desktop GUI
│       ├── windows_startup.py   # Windows integration
│       └── chatbot.py           # Web UI (Gradio)
│
└── [Other SIGRID files...]
```

---

## 🎯 Next Steps

1. **Run Setup:**
   ```bash
   python setup_desktop.py
   ```

2. **Launch Desktop App:**
   ```bash
   python start_desktop.py
   ```

3. **Start Chatting:**
   - Type any command
   - Watch resources in real-time
   - Minimize to tray
   - SIGRID runs 24/7!

---

**SIGRID Desktop** - Your AI assistant that lives on your desktop, monitors your system, and learns from every interaction!
