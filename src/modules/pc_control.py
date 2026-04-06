# PC Control Module - Mouse, Keyboard, Screen Management

import pyautogui
import pydirectinput
from PIL import Image
from datetime import datetime
from pathlib import Path
from src.config.settings import (
    SCREENSHOT_QUALITY,
    MOUSE_SPEED,
    TYPING_INTERVAL,
    SCREENSHOTS_DIR
)
from typing import Optional, Tuple
import time

class PCController:
    """Controls mouse, keyboard, and screen capture."""
    
    def __init__(self):
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = MOUSE_SPEED
        
        # Configure PyDirectInput for better Windows game/app support
        pydirectinput.FAILSAFE = True
        
    def move_mouse(self, x: int, y: int, duration: float = None) -> dict:
        """Move mouse to specific coordinates."""
        speed = duration if duration else MOUSE_SPEED
        pyautogui.moveTo(x, y, duration=speed)
        return {"status": "success", "action": "move_mouse", "position": (x, y)}
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1, button: str = "left") -> dict:
        """Click at current or specified position."""
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
        else:
            pyautogui.click(clicks=clicks, button=button)
        pos = pyautogui.position()
        return {"status": "success", "action": "click", "position": pos, "button": button}
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        """Double-click at current or specified position."""
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
        return {"status": "success", "action": "double_click"}
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        """Right-click at current or specified position."""
        if x is not None and y is not None:
            pyautogui.rightClick(x, y)
        else:
            pyautogui.rightClick()
        return {"status": "success", "action": "right_click"}
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> dict:
        """Scroll up (positive) or down (negative)."""
        pyautogui.scroll(clicks, x=x, y=y)
        return {"status": "success", "action": "scroll", "clicks": clicks}
    
    def drag_to(self, x: int, y: int, duration: float = 0.5) -> dict:
        """Click and drag to a position."""
        pyautogui.drag(x, y, duration=duration)
        return {"status": "success", "action": "drag_to", "target": (x, y)}
    
    def type_text(self, text: str, interval: float = None) -> dict:
        """Type text character by character."""
        typing_interval = interval if interval else TYPING_INTERVAL
        pyautogui.typewrite(text, interval=typing_interval)
        return {"status": "success", "action": "type_text", "text": text}
    
    def press_key(self, key: str) -> dict:
        """Press a single key."""
        pyautogui.press(key)
        return {"status": "success", "action": "press_key", "key": key}
    
    def hotkey(self, *keys: str) -> dict:
        """Press a combination of keys together."""
        pyautogui.hotkey(*keys)
        return {"status": "success", "action": "hotkey", "keys": list(keys)}
    
    def key_down(self, key: str) -> dict:
        """Hold a key down."""
        pyautogui.keyDown(key)
        return {"status": "success", "action": "key_down", "key": key}
    
    def key_up(self, key: str) -> dict:
        """Release a held key."""
        pyautogui.keyUp(key)
        return {"status": "success", "action": "key_up", "key": key}
    
    def get_mouse_position(self) -> dict:
        """Get current mouse position."""
        x, y = pyautogui.position()
        return {"status": "success", "action": "get_position", "position": (x, y)}
    
    def get_screen_size(self) -> dict:
        """Get screen resolution."""
        width, height = pyautogui.size()
        return {"status": "success", "action": "screen_size", "width": width, "height": height}
    
    def take_screenshot(self, save: bool = True, region: Optional[Tuple[int, int, int, int]] = None) -> dict:
        """Take a screenshot of the entire screen or a region."""
        try:
            screenshot = pyautogui.screenshot(region=region)
            
            if save:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"
                screenshot.save(str(filepath), quality=SCREENSHOT_QUALITY)
                return {
                    "status": "success",
                    "action": "screenshot",
                    "path": str(filepath),
                    "size": screenshot.size
                }
            
            return {"status": "success", "action": "screenshot", "image": screenshot, "size": screenshot.size}
        except Exception as e:
            return {"status": "error", "action": "screenshot", "error": str(e)}
    
    def locate_on_screen(self, image_path: str, confidence: float = 0.8) -> dict:
        """Find an image on the screen."""
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return {
                    "status": "success",
                    "action": "locate",
                    "position": center,
                    "region": location
                }
            return {"status": "not_found", "action": "locate"}
        except Exception as e:
            return {"status": "error", "action": "locate", "error": str(e)}
    
    def wait_for_image(self, image_path: str, timeout: int = 10, confidence: float = 0.8) -> dict:
        """Wait for an image to appear on screen."""
        try:
            location = pyautogui.waitFor(image_path, timeout=timeout, confidence=confidence)
            if location:
                return {"status": "success", "action": "wait_for_image", "position": location}
            return {"status": "timeout", "action": "wait_for_image"}
        except Exception as e:
            return {"status": "error", "action": "wait_for_image", "error": str(e)}
    
    def execute_action(self, action_name: str, **kwargs) -> dict:
        """Execute a PC control action by name."""
        action_map = {
            "move_mouse": self.move_mouse,
            "click": self.click,
            "double_click": self.double_click,
            "right_click": self.right_click,
            "scroll": self.scroll,
            "drag_to": self.drag_to,
            "type_text": self.type_text,
            "press_key": self.press_key,
            "hotkey": self.hotkey,
            "key_down": self.key_down,
            "key_up": self.key_up,
            "get_mouse_position": self.get_mouse_position,
            "get_screen_size": self.get_screen_size,
            "take_screenshot": self.take_screenshot,
        }
        
        if action_name in action_map:
            return action_map[action_name](**kwargs)
        return {"status": "error", "error": f"Unknown action: {action_name}"}
