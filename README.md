# 🧠 SIGRID AI Control

**S**elf-**I**mproving **G**enerative **R**easoning & **I**ntelligent **D**ecision system

> Advanced desktop AI agent with autonomous learning, PC control, and self-improvement capabilities.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Mojo](https://img.shields.io/badge/Mojo-Experimental-orange.svg)
![License](https://img.shields.io/badge/License-Private-red.svg)
![AI](https://img.shields.io/badge/AI-Gemma_4-orange.svg)
![Framework](https://img.shields.io/badge/Framework-LangGraph-green.svg)
![GUI](https://img.shields.io/badge/GUI-PyQt6-purple.svg)

---

## ✨ Features

### 🖥️ Desktop Application
- **Professional GUI** with PyQt6 and dark theme (Catppuccin Mocha)
- **Real-time chat** with typing indicators and message history
- **System tray** integration with quick actions
- **Windows auto-start** support
- **Minimize to tray** (keeps running in background)

### 📊 Real-Time Resource Monitor
- **CPU** usage, cores, frequency
- **Memory (RAM)** usage and availability
- **Disk** space monitoring (C: drive)
- **GPU** detection (NVIDIA support)
- **Network** traffic (upload/download)
- **Top processes** by CPU usage

### 🧠 Dual AI Engine
- **Google Gemma 4** - Primary AI model via API
- **Qwen CLI** - Secondary AI engine (optional)
- **Intelligent routing** between engines
- **Automatic fallback** on failure

### 🤖 PC Control
- **Mouse automation** - Move, click, drag, scroll
- **Keyboard input** - Type text, press keys, hotkeys
- **Screenshots** - Capture and analyze screen
- **File system** - Read, write, search, copy, move, delete
- **Browser automation** - Playwright-powered web interaction

### 🎯 Advanced Learning Systems

#### ⚡ High-Performance Layer (Mojo)
- **Native-speed image processing** - Screenshot analysis 10-100x faster than Python
- **Visual root cause analysis** - Detect UI elements, changes, and layout issues
- **Task queue orchestration** - Low-latency agent coordination
- **Sandboxed execution** - Safe AI-generated code testing
- **Automatic Python fallback** - Works without Mojo installed

#### Reinforcement Learning
- **Action recording** with results and execution time
- **User feedback loop** - Rate actions success/failure
- **Prompt optimization** - Weights adjust based on performance
- **Performance tracking** - Success rates per action type
- **Automatic selection** of best prompts

#### Self-Improvement Engine
- **Autonomous failure diagnosis** and root cause analysis
- **Code generation** - Writes patches and fixes
- **Prompt enhancement** - Improves instructions automatically
- **New capability creation** - Generates entirely new modules
- **Architecture evolution** - Suggests system improvements

### 🎤 Voice Interface
- **Speech-to-text** recognition
- **Text-to-speech** responses
- **Hands-free operation**
- **Continuous listening mode**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google AI API key (from [Google AI Studio](https://aistudio.google.com))
- Windows OS (for full desktop features)

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Sigrid-AI-Control.git
cd Sigrid-AI-Control

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Configure API key (edit .env file)
# GOOGLE_API_KEY=your_api_key_here

# Run setup wizard (recommended)
python setup_desktop.py
```

### Launch

**Option 1: Desktop App (Recommended)**
```bash
python start_desktop.py
```

**Option 2: CLI Mode**
```bash
python main.py
```

**Option 3: Web UI**
```bash
python main.py
# Choose option 2 at prompt
```

---

## 📁 Project Structure

```
Sigrid-AI-Control/
├── main.py                      # Main entry point (3 modes)
├── start_desktop.py             # Desktop app launcher
├── setup_desktop.py             # Setup wizard
├── requirements.txt             # Python dependencies
├── .env                         # Configuration & API keys
│
├── src/
│   ├── ai_client.py             # Dual AI engine (Gemma 4 + Qwen)
│   │
│   ├── config/
│   │   └── settings.py          # System configuration
│   │
│   ├── agents/
│   │   └── orchestrator.py      # LangGraph multi-agent system
│   │                             # + RL + Self-Improvement
│   │
│   ├── modules/
│   │   ├── pc_control.py        # Mouse, keyboard, screenshots
│   │   ├── file_system.py       # File/directory operations
│   │   ├── browser.py           # Playwright web automation
│   │   └── voice.py             # Speech recognition & TTS
│   │
│   ├── learning/                # 🧪 LEARNING SYSTEMS
│   │   ├── prompt_optimizer.py  # Reinforcement learning
│   │   └── self_improvement.py  # Autonomous code generation
│   │
│   └── ui/
│       ├── desktop_app.py       # PyQt6 desktop application
│       ├── windows_startup.py   # Windows auto-start integration
│       └── chatbot.py           # Gradio web interface
│
├── docs/
│   ├── ARCHITECTURE.md          # Technical architecture
│   ├── DESKTOP_APP.md           # Desktop app guide
│   └── QUICKSTART.md            # Getting started guide
│
├── memory/                      # Auto-generated learning data
├── logs/                        # System logs
└── screenshots/                 # Captured screenshots
```

---

## 🎯 Usage Examples

### Desktop App Commands

**Basic:**
```
Take a screenshot
List files in my Documents folder
Create a new file called test.txt with "Hello World"
Open google.com and search for Python tutorials
```

**Learning:**
```
learning      → Show learning system status
feedback      → Rate last action (success/failure)
improvements  → View self-improvement log
```

### System Tray Quick Actions
- 📸 **Take Screenshot** - Instant capture
- 📁 **List Documents** - Quick file browser
- Double-click tray icon → Restore window
- Close button → Minimize to tray (doesn't quit)

---

## 🧬 Architecture

### Multi-Agent System (LangGraph)

```
User Input → Route Node → Route Decision
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
              PC Control          File System
              Browser             Orchestrator
                    └─────────┬─────────┘
                              ↓
                    [Prompt Optimizer] ← RL System
                              ↓
                    [Execute Action]
                              ↓
                    Success? → No → [Self-Improvement]
                              ↓
                        Respond
```

### Learning Flow

```
1. User makes request
2. SIGRID selects optimized prompt (weighted by RL)
3. Action executes
4. Result recorded with timing
5. User provides feedback (optional)
6. Prompt weights adjust:
   - Success: weight *= 1.1
   - Failure: weight *= 0.9
7. On failure → Self-Improvement generates fixes
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Google AI API
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemma-4-4b-it
MODEL_TEMPERATURE=0.7

# Voice
VOICE_LANGUAGE=en-US
VOICE_RATE=200

# PC Control
SCREENSHOT_QUALITY=85
MOUSE_SPEED=0.3
TYPING_INTERVAL=0.05

# Browser
BROWSER_HEADLESS=false
```

### Windows Auto-Start

```bash
# Enable
python src/ui/windows_startup.py --enable

# Disable
python src/ui/windows_startup.py --disable

# Check status
python src/ui/windows_startup.py --status
```

---

## 📊 Learning Metrics

SIGRID tracks comprehensive performance data:

| Metric | Description |
|--------|-------------|
| **Success Rate** | % of successful actions |
| **Avg Reward** | Weighted score (success + speed) |
| **Prompt Performance** | Best-performing templates |
| **Self-Improvements** | Autonomous fixes generated |
| **Learning Rate** | % of improvements applied |

**Expected Convergence:**
- Initial: ~70% success
- After 50 interactions: ~85%
- After 200 interactions: ~92%

---

## 🔐 Security Features

- **Failsafe controls** - Move mouse to corner to abort
- **Permission validation** - Before sensitive operations
- **Execution timeouts** - Prevents runaway processes
- **Input sanitization** - Path traversal prevention
- **Confirmation prompts** - For destructive actions
- **API key protection** - `.env` file in `.gitignore`

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **AI Models** | Google Gemma 4, Qwen CLI |
| **Agent Framework** | LangGraph (LangChain) |
| **Desktop GUI** | PyQt6 |
| **Web UI** | Gradio |
| **Browser** | Playwright |
| **PC Control** | PyAutoGUI, PyDirectInput |
| **Voice** | pyttsx3, SpeechRecognition |
| **System Monitor** | psutil |
| **Language** | Python 3.10+ |

---

## 📖 Documentation

- **[README.md](README.md)** - This file (overview)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete technical architecture
- **[docs/DESKTOP_APP.md](docs/DESKTOP_APP.md)** - Desktop application guide
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Getting started tutorial

---

## 🎓 Research Foundation

Built on cutting-edge AI research:
- **LangGraph**: Graph-based agent orchestration
- **RLHF**: Reinforcement Learning from Human Feedback
- **Self-Improving AI**: Autonomous code generation
- **Multi-Agent Systems**: Specialized agent coordination
- **State Machines**: Explicit workflow control

---

## ⚠️ Important Notes

- **Private Repository** - Contains API keys and personal configurations
- **Do Not Share** `.env` file publicly
- **Windows Only** - Full desktop features require Windows
- **AI Costs** - API usage incurs charges based on tokens

---

## 🚀 Future Enhancements

- [ ] Multi-monitor support
- [ ] Advanced RAG (Retrieval-Augmented Generation)
- [ ] Custom agent marketplace
- [ ] Persistent memory across sessions
- [ ] Mobile companion app
- [ ] Plugin system for extensions
- [ ] Advanced scheduling and planning

---

## 📝 License

**Private & Confidential** - All rights reserved.

This software is proprietary and not for distribution without explicit permission.

---

**SIGRID** - Not just an AI assistant, but a self-evolving intelligent system.

*Powered by Google Gemma 4, LangGraph, PyQt6, and Advanced Machine Learning*
