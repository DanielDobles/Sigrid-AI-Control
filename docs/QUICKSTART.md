# 🚀 SIGRID Quick Start Guide

## What is SIGRID?

**SIGRID** (Self-Improving Generative Reasoning & Intelligent Decision system) is an advanced AI agent system that:

1. **Controls Your PC** - Mouse, keyboard, files, browser
2. **Learns From You** - Reinforcement learning via feedback
3. **Improves Itself** - Autonomous code generation and optimization
4. **Dual AI Engine** - Google Gemma 4 + Qwen CLI

## 🎯 Quick Start (3 Steps)

### Step 1: Verify Installation

```bash
cd C:\Users\armon\DEV\Sigrid-AI-Control

# Verify all modules
python -c "from src.agents.orchestrator import SigridOrchestrator; print('✅ Ready')"
```

### Step 2: Start SIGRID

```bash
python main.py
```

You'll see:
```
╔══════════════════════════════════════════════════════════╗
║              S.I.G.R.I.D.  A I  C O N T R O L           ║
║  Google Gemma 4 + Qwen CLI + LangGraph + RL Learning     ║
╚══════════════════════════════════════════════════════════╝

👋 SIGRID Online
┌─────────────────────────────────────────────────────────┐
│ Good day! I'm SIGRID, your personal AI assistant.      │
│                                                          │
│ I'm fully operational and ready to help you with:       │
│   📁 File System - Read, write, search, manage files    │
│   🖱️  PC Control - Mouse, keyboard, screenshots         │
│   🌐 Browser - Navigate websites, extract data          │
│   💻 Terminal - Execute commands                        │
│   🎤 Voice - Speak with me using voice commands         │
│                                                          │
│ How can I assist you today?                              │
└─────────────────────────────────────────────────────────┘
```

### Step 3: Start Interacting!

**Choose Interface:**
- Type `1` for CLI Mode (Terminal)
- Type `2` for Web UI (Browser)

## 💡 First Commands to Try

### Basic Commands

```
You → Take a screenshot
You → List files in my Documents folder
You → What's my screen resolution?
You → Create a new file called test.txt with "Hello World"
```

### Learning Commands

```
You → learning
┌─────────────────────────────────┐
│ 📊 Learning Status              │
│                                 │
│ Total Interactions: 0           │
│ Success Rate: 0.0%              │
│ Self-Improvements: 0            │
└─────────────────────────────────┘

You → feedback
┌─────────────────────────────────┐
│ 💬 Feedback Request             │
│                                 │
│ Last Action: pc_control         │
│ Was it successful? (y/n):       │
└─────────────────────────────────┘

You → improvements
┌─────────────────────────────────┐
│ 🔧 Self-Improvement Log         │
│                                 │
│ No improvements yet.            │
│ SIGRID will learn as you use it!│
└─────────────────────────────────┘
```

## 🧪 Testing the Learning System

### Test Reinforcement Learning

1. **Make a Request:**
   ```
   You → Take a screenshot
   ```

2. **Provide Feedback:**
   ```
   You → feedback
   
   Was this action successful? (y/n): y
   Additional feedback (optional): Perfect!
   
   ✅ Feedback recorded! Reward: 1.20
   ```

3. **Check Learning:**
   ```
   You → learning
   
   📊 Learning Status
   ┌─────────────────────────────┐
   │ Total Interactions: 1       │
   │ Success Rate: 100.0%        │
   │ Successful Actions: 1       │
   └─────────────────────────────┘
   ```

### Test Self-Improvement

1. **Make a Complex Request** (one that might fail):
   ```
   You → Click the submit button on google.com
   ```

2. **If it Fails, SIGRID Automatically:**
   - Diagnoses the problem
   - Generates an improvement strategy
   - Creates code/prompt fixes
   - Logs the improvement

3. **View Improvements:**
   ```
   You → improvements
   
   🔧 Self-Improvement Log
   - imp_20260406_123456_browser
     Type: prompt_enhancement
     Status: generated
   ```

## 🎤 Voice Mode

```
You → voice

🎤 Listening...
(You speak)
📝 Recognized: take a screenshot

(SIGRID processes voice command)
```

## 🌐 Web UI Mode

If you choose option 2 at startup:
- Opens browser at `http://127.0.0.1:7860`
- Chat interface with SIGRID
- Same capabilities as CLI
- Better for visual tasks

## 🔧 Configuration

### Change AI Model

Edit `.env`:
```env
# Switch to different Google model
MODEL_NAME=gemma-3-27b-it

# Or use Qwen CLI by default
# (Set use_qwen=True in code)
```

### Adjust Learning Speed

Edit `src/learning/prompt_optimizer.py`:
```python
# Faster learning (more aggressive)
SUCCESS_MULTIPLIER = 1.2  # Was 1.1
FAILURE_MULTIPLIER = 0.8  # Was 0.9

# Slower learning (more conservative)
SUCCESS_MULTIPLIER = 1.05
FAILURE_MULTIPLIER = 0.95
```

## 📊 Monitoring Progress

### After 10+ Interactions

```
You → learning

📊 Learning Status
┌──────────────────────────────┐
│ Reinforcement Learning       │
│ - Total Interactions: 25     │
│ - Success Rate: 84.0%        │
│ - Best: file_system (0.95)   │
│ - Needs work: browser (0.72) │
│                              │
│ Self-Improvement             │
│ - Total: 8                   │
│ - Applied: 5                 │
│ - Learning Rate: 62.5%       │
└──────────────────────────────┘
```

### Analyze Failures

```python
# In Python console or script
from src.agents.orchestrator import SigridOrchestrator

orchestrator = SigridOrchestrator()
failures = orchestrator.prompt_optimizer.analyze_failures()

for failure in failures:
    print(f"Action: {failure['action_type']}")
    print(f"Error: {failure['error']}")
    print(f"Suggestion: {failure['suggestion']}")
```

## 🎯 Best Practices

### For Better Learning

1. **Always Provide Feedback**
   - Use `feedback` command after actions
   - Be specific about what went wrong

2. **Be Clear in Requests**
   - "Take a screenshot" ✓
   - "Do something with my screen" ✗

3. **Review Improvements**
   - Use `improvements` regularly
   - See what SIGRID learned
   - Apply code improvements when safe

### For Complex Tasks

1. **Break Down Complex Requests:**
   ```
   You → First, take a screenshot
   (feedback: success)
   
   You → Now, open google.com
   (feedback: success)
   
   You → Search for "Python tutorials"
   ```

2. **Use Learning Commands:**
   ```
   You → learning  (Check status)
   You → feedback  (Rate actions)
   You → improvements  (See what changed)
   ```

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not set"
- Check `.env` file exists
- Verify API key is correct
- Restart SIGRID

### "Qwen CLI not available"
- This is optional
- SIGRID works fine with just Google AI
- Install Qwen CLI if needed

### Voice Not Working
- Install PyAudio: `pip install pyaudio`
- Check microphone permissions
- Windows: Install microphone drivers

### Browser Automation Fails
- Run: `playwright install chromium`
- Check if Chromium installed correctly
- Try with `BROWSER_HEADLESS=false` in `.env`

## 📚 Next Steps

1. **Read Full Documentation:**
   - `README.md` - Complete feature guide
   - `docs/ARCHITECTURE.md` - Technical architecture

2. **Explore Advanced Features:**
   - Custom agent creation
   - Manual prompt optimization
   - Self-improvement application

3. **Monitor Learning:**
   - Check `memory/rl_memory.json`
   - Review `memory/self_improvements.json`
   - Watch success rate improve

## 🎓 Understanding the Learning Systems

### Reinforcement Learning (Simple)
```
You make request → SIGRID acts → You rate it → SIGRID learns
```

### Self-Improvement (Advanced)
```
Action fails → SIGRID diagnoses → Generates fix → Logs improvement
```

## 🚀 You're Ready!

SIGRID is now ready to use with:
- ✅ Dual AI Engine (Google + Qwen)
- ✅ Reinforcement Learning System
- ✅ Self-Improvement Engine
- ✅ Full PC Control
- ✅ Voice Interface
- ✅ Web UI

**Start with:**
```bash
python main.py
```

**Then try:**
1. Basic commands
2. Check learning status
3. Provide feedback
4. Watch SIGRID improve!

---

**Remember:** SIGRID gets better the more you use it and provide feedback. Every interaction helps it learn!
