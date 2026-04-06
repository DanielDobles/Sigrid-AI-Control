# SIGRID AI Control - System Configuration
# Self-Improving Generative Reasoning & Intelligent Decision system

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# === API Configuration ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# === Model Settings ===
MODEL_NAME = os.getenv("MODEL_NAME", "gemma-3-27b-it")  # Gemma 3/4 via API
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))

# === Voice Settings ===
VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "en-US")
VOICE_RATE = int(os.getenv("VOICE_RATE", "200"))

# === PC Control ===
SCREENSHOT_QUALITY = int(os.getenv("SCREENSHOT_QUALITY", "85"))
MOUSE_SPEED = float(os.getenv("MOUSE_SPEED", "0.3"))
TYPING_INTERVAL = float(os.getenv("TYPING_INTERVAL", "0.05"))

# === Browser ===
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

# === System Paths ===
PROJECT_ROOT = Path(__file__).parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"
MEMORY_DIR = PROJECT_ROOT / "memory"

# Create directories if they don't exist
SCREENSHOTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)

# === Agent Configuration ===
MAX_AGENT_ITERATIONS = 10
AGENT_TIMEOUT_SECONDS = 120
CHECKPOINT_ENABLED = True

# === Logging ===
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "jarvis.log"
