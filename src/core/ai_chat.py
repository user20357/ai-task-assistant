"""
AI Chat Manager - Handles conversation with user and task understanding
Uses OpenAI GPT for intelligent conversation and task breakdown.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import openai

logger = logging.getLogger(__name__)

class AIChatManager(QObject):
    """Manages AI-powered chat interactions"""
    
    # Signals
    message_received = pyqtSignal(str, str)  # role, content
    task_ready = pyqtSignal(str)  # task description
    user_needs_help = pyqtSignal(str)  # help request
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Initialize OpenAI client
        self.client = None
        self._init_openai()
        
        # Chat state
        self.conversation_history = []
        self.current_task = ""
        self.task_steps = []
        self.current_step_index = 0
        self.is_floating_mode = False
        
        # System prompts
        self._init_prompts()
        
        logger.info("AIChatManager initialized")
    
    def _init_openai(self):
        """Initialize AI client (OpenAI, Groq, or OpenRouter)"""
        try:
            # Check for Groq API key first
            groq_api_key = os.getenv('GROQ_API_KEY')
            if groq_api_key:
                # Initialize Groq client
                self.client = openai.OpenAI(
                    api_key=groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                
                # Get Groq model from environment or use default
                self.model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
                self.api_type = "groq"
                logger.info(f"Groq client initialized successfully with model: {self.model}")
                return
            
            # Fall back to OpenAI or OpenRouter
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("No API key found in environment variables (GROQ_API_KEY or OPENAI_API_KEY)")
            
            # Support for OpenRouter or OpenAI
            base_url = os.getenv('OPENAI_BASE_URL')
            if base_url:
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                self.api_type = "openrouter" if "openrouter" in base_url else "custom"
                logger.info(f"{self.api_type.capitalize()} client initialized successfully")
            else:
                self.client = openai.OpenAI(api_key=api_key)
                self.api_type = "openai"
                logger.info("OpenAI client initialized successfully")
            
            # Get model from environment or use default
            self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            
            # If using OpenRouter, make sure we use a valid free model
            if self.api_type == "openrouter":
                # List of known working free models on OpenRouter
                free_models = [
                    'google/gemma-2-9b-it:free',
                    'anthropic/claude-3-haiku:free',
                    'mistralai/mistral-7b-instruct:free',
                    'google/gemma-7b-it:free',
                    'xai/grok-1:free'
                ]
                
                # If current model isn't in the free list, use a default free model
                if self.model not in free_models:
                    self.model = 'xai/grok-1:free'
            
            logger.info(f"Using model: {self.model}")
            
        except Exception as e:
            logger.error("Failed to initialize AI client: " + str(e))
            self.error_occurred.emit("AI initialization failed: " + str(e))
    
    def _init_prompts(self):
        """Initialize system prompts"""
        self.system_prompt = """You are a helpful AI assistant that guides users through computer tasks step-by-step with visual guidance.

Your role:
1. Understand what task the user wants to accomplish
2. Ask 1-2 clarifying questions if needed (don't over-ask)
3. Once you understand the basic task, indicate you're ready to provide visual guidance
4. Break down the task into clear, simple steps during guidance

Guidelines:
- Keep initial questions brief - you can clarify details during guidance
- After understanding the task, say something like "I'm ready to guide you!" or "Let's get started!"
- Be encouraging and mention that you'll provide visual guidance with RED SQUARES
- Don't ask too many prerequisites upfront - focus on getting started

Important: Once you understand what the user wants to do, indicate readiness by saying phrases like:
- "I'm ready to guide you through this!"
- "Let's get started with the visual guidance!"
- "Ready to help you step-by-step!"

When you're ready to start guidance, you should also think about the steps needed to complete the task, but don't list them to the user yet. You'll guide them one step at a time with visual cues.

Current phase: Initial conversation to understand the task."""

        self.guidance_prompt = """You are now in VISUAL GUIDANCE mode. The user has RED SQUARES highlighting clickable elements on their screen.

Your role:
- Give specific instructions about which RED SQUARE to click
- Reference the detected elements by their labels/positions  
- Provide step-by-step guidance with visual cues
- Wait for user to click before proceeding

Guidelines:
- Say "Click the RED SQUARE around [element name]"
- Reference specific UI elements detected by YOLO (Chrome icon, close button, etc.)
- Give ONE instruction at a time
- Be very specific about which red square to click
- Ask "Did you click it?" after each instruction

Example: "Click the RED SQUARE around the Chrome icon to open browser"

Remember that you are guiding the user through a series of steps to complete their task. Keep track of where they are in the process and what the next logical step should be based on what's visible on their screen.

Current phase: Active visual guidance with RED SQUARE overlays."""

        self.task_planning_prompt = """You are a task planning AI that breaks down computer tasks into clear, actionable steps.

Given a user's task description, create a detailed step-by-step plan.

IMPORTANT: You MUST respond with ONLY a valid JSON array. No other text, explanations, or formatting.

Format your response as a JSON array of steps, where each step has:
- step_number: The sequence number (integer)
- action: What to do (string: "click", "type", "drag", "open", etc.)
- target: What UI element to interact with (string)
- description: Detailed description of this step (string)
- expected_result: What should happen after this step (string)

Example response format:
[{"step_number":1,"action":"click","target":"Chrome icon","description":"Click on the Chrome browser icon in the taskbar or desktop","expected_result":"Chrome browser opens"},{"step_number":2,"action":"type","target":"address bar","description":"Click in the address bar and type gmail.com","expected_result":"The URL is entered in the address bar"}]

Rules:
- Respond with ONLY the JSON array
- No code blocks, no explanations, no extra text
- Use double quotes for all strings
- Ensure valid JSON syntax
- Keep descriptions clear and concise
- Focus on specific UI elements the user will interact with"""
    def start_session(self) -> bool:
        """Start a new chat session"""
        try:
            self.conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Send welcome message
            welcome_msg = "Hi! I'm your AI Task Assistant. I'll help you complete computer tasks step-by-step.\n\nWhat would you like to accomplish today? For example:\n- Upload a document to a website\n- Fill out an online form\n- Search for information online\n- Set up software or accounts\n\nJust tell me what you need to do, and I'll guide you through it!"
            
            self.message_received.emit("assistant", welcome_msg)
            return True
            
        except Exception as e:
            logger.error("Failed to start session: " + str(e))
            self.error_occurred.emit("Session start failed: " + str(e))
            return False
    
    def send_message(self, message: str) -> str:
        """Send user message and get AI response"""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Emit the response
            self.message_received.emit("assistant", ai_response)
            
            # Check if task is ready to start
            self._check_task_readiness(ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error("Failed to send message: " + str(e))
            error_msg = "Sorry, I encountered an error: " + str(e)
            self.error_occurred.emit(error_msg)
            return error_msg
    
    def _check_task_readiness(self, ai_response: str):
        """Check if AI indicates task is ready to start"""
        # Check if user has described a task (at least 2 exchanges)
        user_messages = [msg for msg in self.conversation_history if msg['role'] == 'user']
        ai_messages = [msg for msg in self.conversation_history if msg['role'] == 'assistant']
        
        # Check if AI has responded with a "let's start" or similar phrase
        ready_phrases = ["let's start", "let's begin", "ready to start", "ready to begin", 
                         "i can help", "i'll help", "i will help", "let me help", "ready to guide"]
        
        if len(user_messages) >= 1 and len(ai_messages) >= 1 and not hasattr(self, '_task_ready_emitted'):
            # Check if AI's last message contains a ready phrase
            last_ai_message = ai_messages[-1]['content'].lower()
            is_ready = any(phrase in last_ai_message for phrase in ready_phrases)
            
            if is_ready:
                # Extract task description
                task_desc = self._extract_task_description()
                if task_desc:
                    self.current_task = task_desc
                    
                    # Generate task steps before starting guidance
                    logger.info(f"Generating task steps for: {task_desc}")
                    self.task_steps = self.generate_task_steps(task_desc)
                    self.current_step_index = 0
                    
                    if self.task_steps:
                        logger.info(f"Generated {len(self.task_steps)} steps for task")
                    else:
                        logger.warning("Failed to generate task steps, will use dynamic guidance")
                    
                    self._task_ready_emitted = True
                    self.task_ready.emit(task_desc)
                    logger.info(f"Task ready: {task_desc}")
    
    def _extract_task_description(self) -> str:
        """Extract task description from conversation history"""
        try:
            # Look for user's initial task description
            for msg in self.conversation_history:
                if msg["role"] == "user" and len(msg["content"]) > 20:
                    return msg["content"][:200]  # First substantial user message
            return "User task"
        except:
            return "User task"
    
    def switch_to_floating_mode(self):
        """Switch to floating chat mode for guidance"""
        self.is_floating_mode = True
        
        # Update system prompt for guidance mode if not already done
        if self.conversation_history[0]["content"] != self.guidance_prompt:
            self.conversation_history[0]["content"] = self.guidance_prompt
        guidance_msg = "🎯 Guidance mode activated!\n\nI'm now watching your screen and will guide you step-by-step. You can:\n- Ask me questions anytime\n- Say 'I'm stuck' if you need help\n- Say 'pause' to pause guidance\n- Say 'stop' to end guidance\n\nLet's start with the first step!"
        
        self.message_received.emit("assistant", guidance_msg)
    
    def switch_to_normal_mode(self):
        """Switch back to normal chat mode"""
        self.is_floating_mode = False
        self.conversation_history[0]["content"] = self.system_prompt
    
    def get_current_step_guidance(self, detections: List[Dict]) -> Dict[str, Any]:
        """Get guidance for current step based on screen detections"""
        try:
            if not detections:
                return {"instruction": "Looking for elements on screen...", "priority_elements": []}
            
            # Create context about detected elements
            elements_context = "Detected screen elements:\n"
            for i, detection in enumerate(detections):
                elements_context += "- " + str(detection.get('label', 'Unknown')) + ": " + str(detection.get("action", "No action")) + "\n"
            
            # Ask AI what to do with these elements - emphasize RED SQUARES
            guidance_request = "I can see RED SQUARES highlighting these clickable elements:\n" + elements_context + "\n\nBased on our task \"" + str(self.current_task) + "\", which RED SQUARE should I click next?\nProvide:\n1. Clear instruction mentioning \"RED SQUARE around [element]\"\n2. Which specific red square to click\n3. What will happen after clicking\n\nExample: \"Click the RED SQUARE around the Chrome icon to open the browser\"\n\nKeep it simple and actionable."
            
            # Get AI guidance
            self.conversation_history.append({"role": "user", "content": guidance_request})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[-3:],  # Last few messages for context
                max_tokens=200,
                temperature=0.3
            )
            
            guidance = response.choices[0].message.content
            
            # Parse guidance (simplified)
            return {
                "instruction": guidance,
                "priority_elements": [d for d in detections if "button" in d.get('label', '').lower() or "click" in d.get('action', '').lower()]
            }
            
        except Exception as e:
            logger.error("Failed to get step guidance: " + str(e))
            return {
                "instruction": "Continue with your task. Ask me if you need help!",
                "priority_elements": detections[:2]  # Show first 2 elements
            }
    
    def handle_user_action(self, element_info: Dict[str, Any]):
        """Handle user clicking on an element"""
        try:
            element_label = element_info.get('label', 'element')
            action_msg = f"User clicked on: {element_label}"
            
            # Add to conversation for context
            self.conversation_history.append({"role": "user", "content": action_msg})
            
            # If we have task steps, advance to the next step
            if self.task_steps and self.current_step_index < len(self.task_steps) - 1:
                # Move to next step
                self.current_step_index += 1
                current_step = self.task_steps[self.current_step_index]
                
                # Create a message about the next step
                step_description = current_step.get('description')
                next_step_msg = f"Great! Now let's move to step {self.current_step_index + 1}:\n{step_description}"
                self.message_received.emit("assistant", next_step_msg)
                
                logger.info(f"Advanced to step {self.current_step_index + 1} of {len(self.task_steps)}")
                return
            
            # If we don't have steps or reached the end, get dynamic guidance
            element_label = element_info.get('label', 'an element')
            next_step_request = f"User just clicked on {element_label}. What should they do next for the task: {self.current_task}?"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history[-2:] + [{"role": "user", "content": next_step_request}],
                max_tokens=150,
                temperature=0.3
            )
            
            next_guidance = response.choices[0].message.content
            self.message_received.emit("assistant", "Great! " + next_guidance)
            
        except Exception as e:
            logger.error("Failed to handle user action: " + str(e))
    
    def get_help_response(self, help_request: str) -> str:
        """Get help response for user's question"""
        try:
            help_context = "User needs help during task " + str(self.current_task) + ". They said: " + str(help_request)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.guidance_prompt},
                    {"role": "user", "content": help_context}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            help_response = response.choices[0].message.content
            self.message_received.emit("assistant", help_response)
            return help_response
            
        except Exception as e:
            logger.error("Failed to get help response: " + str(e))
            return "I'm here to help! Can you tell me more specifically what you're having trouble with?"
    
    def is_active(self) -> bool:
        """Check if chat is active"""
        return len(self.conversation_history) > 1
    
    def generate_task_steps(self, task_description: str) -> List[Dict[str, Any]]:
        """Generate detailed steps for completing the task"""
        try:
            logger.info(f"Generating task steps for: {task_description}")
            
            # Create a special conversation just for task planning
            planning_messages = [
                {"role": "system", "content": self.task_planning_prompt},
                {"role": "user", "content": f"Create a step-by-step plan for this task: {task_description}"}
            ]
            
            # Get response from AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=planning_messages,
                temperature=0.2,  # Lower temperature for more consistent planning
                max_tokens=2000
            )
            
            # Extract the response content
            plan_text = response.choices[0].message.content
            
            # Try to parse JSON from the response
            try:
                # Clean the response text
                plan_text = plan_text.strip()
                
                # Find JSON array in the response using multiple patterns
                import re
                json_patterns = [
                    r'\[\s*\{.*?\}\s*\]',  # Standard JSON array
                    r'```json\s*(\[.*?\])\s*```',  # JSON in code blocks
                    r'```\s*(\[.*?\])\s*```',  # JSON in generic code blocks
                ]
                
                extracted_json = None
                for pattern in json_patterns:
                    match = re.search(pattern, plan_text, re.DOTALL)
                    if match:
                        if match.groups():
                            extracted_json = match.group(1)
                        else:
                            extracted_json = match.group(0)
                        break
                
                if extracted_json:
                    # Clean up common JSON issues
                    extracted_json = extracted_json.replace('\n', ' ')
                    extracted_json = re.sub(r'\\(?!["\\/bfnrt])', r'\\\\', extracted_json)  # Fix invalid escapes
                    
                    # Parse the JSON
                    steps = json.loads(extracted_json)
                    if isinstance(steps, list) and len(steps) > 0:
                        logger.info(f"Successfully generated {len(steps)} task steps")
                        return steps
                
                # If no JSON found, try to parse the entire response
                steps = json.loads(plan_text)
                logger.info(f"Successfully generated {len(steps)} task steps")
                return steps
                
            except (json.JSONDecodeError, Exception) as e:
                logger.error("Failed to parse task steps JSON: " + str(e))
                logger.debug(f"Raw response: {plan_text[:500]}...")
                
                # Fall back to parsing the text manually
                return self._parse_steps_from_text(plan_text)
                
        except Exception as e:
            logger.error("Failed to generate task steps: " + str(e))
            return []
    
    def _parse_steps_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse steps from plain text when JSON parsing fails"""
        try:
            steps = []
            lines = text.split('\n')
            current_step = {}
            step_number = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for step indicators
                if any(indicator in line.lower() for indicator in ['step', 'click', 'open', 'type', 'navigate']):
                    if current_step:
                        steps.append(current_step)
                    
                    current_step = {
                        "step_number": step_number,
                        "action": "click",
                        "target": "UI element",
                        "description": line,
                        "expected_result": "Continue to next step"
                    }
                    step_number += 1
                elif current_step and len(line) > 10:
                    # Add additional description
                    current_step["description"] += f" {line}"
            
            # Add the last step
            if current_step:
                steps.append(current_step)
            
            # If no steps found, create a default one
            if not steps:
                steps = [
                    {
                        "step_number": 1,
                        "action": "click",
                        "target": "relevant UI element",
                        "description": "Follow the visual guidance with RED SQUARES",
                        "expected_result": "Complete the task step by step"
                    }
                ]
            
            logger.info(f"Parsed {len(steps)} steps from text")
            return steps
            
        except Exception as e:
            logger.error("Failed to parse steps from text: " + str(e))
            return [
                {
                    "step_number": 1,
                    "action": "click",
                    "target": "relevant UI element",
                    "description": "Follow the visual guidance with RED SQUARES",
                    "expected_result": "Complete the task step by step"
                }
            ]
    
    def switch_to_guidance_mode(self):
        """Switch to guidance mode and prepare first step"""
        try:
            # Update system prompt to guidance mode
            self.conversation_history.append({"role": "system", "content": self.guidance_prompt})
            
            # If we have task steps, start with the first one
            if self.task_steps and len(self.task_steps) > 0:
                first_step = self.task_steps[0]
                self.current_step_index = 0
                
                # Create a message about the first step
                first_step_msg = f"Let's start with step 1 of {len(self.task_steps)}:\n{first_step.get('description')}\n\nLook for RED SQUARES that highlight where to click."
                self.message_received.emit("assistant", first_step_msg)
                
                logger.info(f"Starting guidance with {len(self.task_steps)} steps")
            else:
                # No steps available, use dynamic guidance
                welcome_msg = "I'll guide you through this task step by step. Look for RED SQUARES that highlight where to click."
                self.message_received.emit("assistant", welcome_msg)
                
                logger.info("Starting guidance with dynamic steps (no pre-generated steps)")
            
            # Set floating mode flag
            self.is_floating_mode = True
            
        except Exception as e:
            logger.error("Failed to switch to guidance mode: " + str(e))
            self.message_received.emit("assistant", "I'll guide you through this task. Look for RED SQUARES on your screen.")
    
    def get_current_step_guidance_with_detections(self, detection_summary: str) -> str:
        """Get guidance for current step with detection context"""
        try:
            # If we don't have task steps yet and we have a current task, generate them
            if not self.task_steps and self.current_task:
                self.task_steps = self.generate_task_steps(self.current_task)
            
            # Get the current step if available
            current_step = None
            if self.task_steps and 0 <= self.current_step_index < len(self.task_steps):
                current_step = self.task_steps[self.current_step_index]
            
            # Create a message that includes both the detection summary and current step context
            message = detection_summary
            if current_step:
                message += f"\n\nCurrent task step ({self.current_step_index + 1} of {len(self.task_steps)}):\n"
                message += f"Action: {current_step.get('action')}\n"
                message += f"Target: {current_step.get('target')}\n"
                message += f"Description: {current_step.get('description')}\n"
                message += f"Expected result: {current_step.get('expected_result')}\n\n"
                message += "Which RED SQUARE should I click to complete this step? Be very specific about which RED SQUARE to click."
            
            # Send detection info to AI for contextual guidance
            response = self.send_message(message)
            return response
        except Exception as e:
            logger.error("Failed to get step guidance: " + str(e))
            return "I can see RED squares on screen. Click the one that matches your task."