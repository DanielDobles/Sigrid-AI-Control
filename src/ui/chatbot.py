# Chatbot UI with Gradio

import gradio as gr
from typing import List, Tuple
from src.agents.orchestrator import JarvisOrchestrator
from src.modules.voice import VoiceController

Message = Tuple[str, str]

class JarvisChatbot:
    """Gradio-based chatbot interface for Jarvis."""
    
    def __init__(self):
        self.orchestrator = JarvisOrchestrator()
        self.voice = VoiceController()
        self.conversation_history: List[Message] = []
        
    def _format_response(self, response_text: str) -> str:
        """Format the AI response for display."""
        # Remove JSON code blocks for cleaner display
        if "```json" in response_text:
            parts = response_text.split("```json")
            main_response = parts[0].strip()
            return main_response if main_response else response_text
        return response_text
    
    def handle_message(self, message: str, history: List[Message]) -> str:
        """Handle incoming chat messages."""
        if not message or not message.strip():
            return "Please provide a valid message."
        
        try:
            # Process through orchestrator
            result = self.orchestrator.process_input(message.strip())
            response = result.get("ai_response", "I'm not sure how to respond.")
            
            # Clean response for display
            clean_response = self._format_response(response)
            
            # Add to history
            self.conversation_history.append((message.strip(), clean_response))
            
            # Speak the response
            self.voice.speak(clean_response, block=False)
            
            return clean_response
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            self.conversation_history.append((message.strip(), error_msg))
            return error_msg
    
    def handle_voice_input(self, audio_file) -> str:
        """Handle voice input from Gradio's audio component."""
        # This would integrate with speech recognition
        # For now, return a placeholder
        return "Voice input received. Text recognition is being processed."
    
    def clear_conversation(self) -> Tuple[List[Message], str]:
        """Clear the conversation history."""
        self.conversation_history = []
        self.orchestrator.gemma_client.clear_chat()
        return [], "Conversation cleared. How can I help you?"
    
    def launch(self):
        """Launch the Gradio chatbot interface."""
        with gr.Blocks(title="JARVIS AI Control", theme=gr.themes.Soft()) as demo:
            gr.Markdown(
                """
                # 🤖 JARVIS AI Control
                ### Your Intelligent Personal Assistant
                
                Control your PC with natural language - files, browser, mouse, keyboard, and more!
                """
            )
            
            chatbot = gr.Chatbot(
                label="Conversation",
                height=500,
                type="tuples"
            )
            
            with gr.Row():
                with gr.Column(scale=4):
                    msg = gr.Textbox(
                        placeholder="Type your message here... (e.g., 'Take a screenshot', 'Open Google', 'List files in Documents')",
                        label="Your Message",
                        lines=2
                    )
                with gr.Column(scale=1):
                    submit_btn = gr.Button("Send", variant="primary")
            
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Conversation")
                voice_btn = gr.Button("🎤 Voice Input")
            
            # Event handlers
            def user_turn(message, history):
                if not message.strip():
                    return "", history
                return "", history + [[message, None]]
            
            def bot_turn(history):
                if not history or not history[-1][1]:
                    return history
                user_message = history[-1][0]
                response = self.handle_message(user_message, history[:-1])
                history[-1][1] = response
                return history
            
            submit_btn.click(
                user_turn,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
                queue=False
            ).then(
                bot_turn,
                inputs=[chatbot],
                outputs=[chatbot],
                queue=True
            )
            
            msg.submit(
                user_turn,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
                queue=False
            ).then(
                bot_turn,
                inputs=[chatbot],
                outputs=[chatbot],
                queue=True
            )
            
            clear_btn.click(
                self.clear_conversation,
                inputs=[],
                outputs=[chatbot, msg]
            )
            
            gr.Markdown(
                """
                ### 💡 Example Commands:
                - "Take a screenshot of my screen"
                - "List all files in my Documents folder"
                - "Open Google and search for Python tutorials"
                - "Create a new folder called 'Projects'"
                - "Move mouse to center of screen"
                - "What's the weather today?"
                """
            )
        
        # Launch the interface
        demo.queue()
        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            inbrowser=True
        )
