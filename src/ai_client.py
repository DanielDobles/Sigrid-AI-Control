# AI Client - Dual Engine: Google Gemma 4 + Qwen CLI

from google import genai
from google.genai import types
from src.config.settings import GOOGLE_API_KEY, MODEL_NAME, MODEL_TEMPERATURE
from typing import Generator, Optional, Dict
import json
import subprocess
import os

class DualAIClient:
    """Manages both Google Gemma 4 and Qwen CLI AI engines."""
    
    def __init__(self):
        self.google_api_key = GOOGLE_API_KEY
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not set. Please add it to .env file.")
        
        # Google Gemma Client
        self.google_client = genai.Client(api_key=self.google_api_key)
        self.model_name = MODEL_NAME
        self.temperature = MODEL_TEMPERATURE
        self.chat = None
        self.system_prompt = None
        
        # Qwen CLI integration
        self.qwen_available = self._check_qwen_availability()
        
    def _check_qwen_availability(self) -> bool:
        """Check if Qwen CLI is available."""
        try:
            result = subprocess.run(
                ["qwen", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def initialize_system_prompt(self, system_instruction: str):
        """Set up the system prompt for the conversation."""
        self.system_prompt = system_instruction
        
    def generate_response(self, prompt: str, max_tokens: int = 2048, use_qwen: bool = False) -> str:
        """Generate a response using either Google or Qwen."""
        if use_qwen and self.qwen_available:
            return self._generate_with_qwen(prompt)
        return self._generate_with_google(prompt, max_tokens)
    
    def _generate_with_google(self, prompt: str, max_tokens: int = 2048) -> str:
        """Generate response using Google Gemma."""
        try:
            # Prepend system prompt to user prompt since gemma-3-27b-it doesn't support system_instruction
            full_prompt = prompt
            if self.system_prompt:
                full_prompt = f"{self.system_prompt}\n\n---\n\nUser Request: {prompt}"
            
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=max_tokens,
            )
            response = self.google_client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            return f"[Error generating response: {str(e)}]"
    
    def _generate_with_qwen(self, prompt: str) -> str:
        """Generate response using Qwen CLI."""
        try:
            result = subprocess.run(
                ["qwen", "chat", "--input", prompt],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                return result.stdout
            return f"[Qwen error: {result.stderr}]"
        except Exception as e:
            return f"[Qwen execution error: {str(e)}]"
    
    def chat_message(self, message: str, max_tokens: int = 2048, use_qwen: bool = False) -> str:
        """Send a message in a chat conversation and get response."""
        if use_qwen and self.qwen_available:
            return self._generate_with_qwen(message)
        
        try:
            # Prepend system prompt to message
            full_message = message
            if self.system_prompt:
                full_message = f"{self.system_prompt}\n\n---\n\nUser Request: {message}"
            
            if not self.chat:
                self.chat = self.google_client.chats.create(
                    model=self.model_name,
                    config=types.GenerateContentConfig(
                        temperature=self.temperature,
                        max_output_tokens=max_tokens,
                    )
                )
            
            response = self.chat.send_message(full_message)
            return response.text
        except Exception as e:
            return f"[Error in chat: {str(e)}]"
    
    def stream_response(self, prompt: str, max_tokens: int = 2048) -> Generator[str, None, None]:
        """Stream response from the model token by token."""
        try:
            full_prompt = prompt
            if self.system_prompt:
                full_prompt = f"{self.system_prompt}\n\n---\n\nUser Request: {prompt}"
            
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=max_tokens,
            )
            response = self.google_client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config,
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"[Error streaming response: {str(e)}]"
    
    def analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze an image using the model's vision capabilities."""
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            full_prompt = prompt
            if self.system_prompt:
                full_prompt = f"{self.system_prompt}\n\n---\n\nUser Request: {prompt}"
            
            config = types.GenerateContentConfig(
                temperature=self.temperature,
            )
            response = self.google_client.models.generate_content(
                model=self.model_name,
                contents=[full_prompt, img],
                config=config,
            )
            return response.text
        except Exception as e:
            return f"[Error analyzing image: {str(e)}]"
    
    def get_chat_history(self) -> list:
        """Retrieve the conversation history."""
        if self.chat:
            return self.chat.history
        return []
    
    def clear_chat(self):
        """Clear the current chat history."""
        self.chat = None
    
    def extract_function_calls(self, response_text: str) -> list:
        """Extract function/tool calls from model response."""
        try:
            # Look for JSON-like function call patterns
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
                return [json.loads(json_str)]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
                if json_str.startswith("{"):
                    return [json.loads(json_str)]
        except:
            pass
        return []
    
    def get_ai_status(self) -> dict:
        """Get status of both AI engines."""
        return {
            "google_gemma": {
                "available": True,
                "model": self.model_name,
                "api_key_set": bool(self.google_api_key)
            },
            "qwen_cli": {
                "available": self.qwen_available,
                "status": "Available" if self.qwen_available else "Not found"
            }
        }
