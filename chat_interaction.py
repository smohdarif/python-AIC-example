"""
Chat interaction sequence using LaunchDarkly AI Configs and AWS Bedrock.

This example demonstrates how to:
- Use LaunchDarkly AI Configs to dynamically manage AI model configurations
- Integrate with AWS Bedrock for chat interactions
- Track metrics and manage conversation state
"""

import os
import json
import re
import time
from typing import List, Dict, Any
import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai.client import LDAIClient, AICompletionConfigDefault
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LaunchDarkly client
LD_SDK_KEY = os.getenv("LAUNCHDARKLY_SDK_KEY")
if not LD_SDK_KEY:
    raise ValueError("LAUNCHDARKLY_SDK_KEY environment variable is required")

ldclient.set_config(Config(LD_SDK_KEY))
ld_client = ldclient.get()
aiclient = LDAIClient(ld_client)

# AWS Configuration
# Uses default AWS credential chain (environment variables, AWS credentials file, IAM roles, etc.)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "aiconfigdemo")

def get_bedrock_client():
    """Get or create AWS Bedrock client."""
    session = boto3.Session(profile_name=AWS_PROFILE)
    return session.client('bedrock-runtime', region_name=AWS_REGION)

# AI Config key - should be created in LaunchDarkly
AI_CONFIG_KEY = os.getenv("LAUNCHDARKLY_AI_CONFIG_KEY", "chat-assistant-config")
JUDGE_CONFIG_KEY = os.getenv("LAUNCHDARKLY_JUDGE_CONFIG_KEY", "ld-ai-judge-accuracy")


class ChatInteraction:
    """Manages chat interactions using LaunchDarkly AI Configs and AWS Bedrock."""
    
    def __init__(self, user_context: Context, ai_config_key: str, judge_config_key: str = None):
        self.user_context = user_context
        self.ai_config_key = ai_config_key
        self.judge_config_key = JUDGE_CONFIG_KEY
        self.conversation_history: List[Dict[str, str]] = []
        self.config = None
        self.tracker = None
        self.judge_config = None
        self.judge_tracker = None
        
    def initialize(self) -> bool:
        """Initialize the AI config from LaunchDarkly."""
        try:
            fallback_value = AICompletionConfigDefault(enabled=False)
            self.config = aiclient.config(
                self.ai_config_key,
                self.user_context,
                fallback_value
            )
            self.tracker = getattr(self.config, "tracker", None)
            
            if not self.config.enabled:
                print("AI Config is disabled for this context.")
                return False
                
            # Initialize conversation with system messages from config
            if self.config.messages:
                self.conversation_history = [
                    {"role": msg.role, "content": msg.content}
                    for msg in self.config.messages
                ]
            
            print(f"AI Config initialized. Model: {self.config.model.name if self.config.model else 'default'}")
            
            # Initialize judge config if available
            self._initialize_judge()
            
            return True
            
        except Exception as e:
            print(f"Error initializing AI config: {e}")
            return False
    
    def _initialize_judge(self):
        """Initialize the judge AI Config from LaunchDarkly."""
        try:
            fallback_value = AICompletionConfigDefault(enabled=False)
            self.judge_config = aiclient.config(
                self.judge_config_key,
                self.user_context,
                fallback_value
            )
            self.judge_tracker = getattr(self.judge_config, "tracker", None)
            
            if not self.judge_config.enabled:
                print(f"Judge config '{self.judge_config_key}' is disabled or not found.")
        except Exception as e:
            print(f"Error initializing judge config: {e}")
            self.judge_config = None
    
    def invoke_bedrock(self, user_message: str) -> Dict[str, Any]:
        """Invoke AWS Bedrock with the user message."""
        if not self.config or not self.config.model:
            raise ValueError("AI Config not initialized or model not configured")
        
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Build messages for converse API
        sys_msgs = [
            {"text": msg["content"]}
            for msg in self.conversation_history
            if msg["role"] == "system"
        ]
        convo_msgs = [
            {
                "role": msg["role"],
                "content": [{"text": msg["content"]}]
            }
            for msg in self.conversation_history
            if msg["role"] != "system"
        ]
        
        params = {
            "modelId": self.config.model.name,
            "messages": convo_msgs,
        }
        
        if sys_msgs:
            params["system"] = sys_msgs
        
        # Add any parameters from the model config
        if hasattr(self.config.model, 'parameters') and self.config.model.parameters:
            if isinstance(self.config.model.parameters, dict):
                params.update(self.config.model.parameters)
        
        start_time = time.time()
        try:
            bedrock_client = get_bedrock_client()
            response = bedrock_client.converse(**params)
            duration = time.time() - start_time
            
            # Extract assistant response
            output = response.get('output', {})
            message = output.get('message', {})
            content = message.get('content', [])
            assistant_message = content[0].get('text', '') if content else ''
            
            # Add assistant response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Track metrics
            if self.tracker:
                try:
                    self.tracker.track_duration(duration)
                    usage = response.get('usage', {})
                    if usage and isinstance(usage, dict):
                        input_tokens = usage.get('inputTokens', 0)
                        output_tokens = usage.get('outputTokens', 0)
                        total_tokens = input_tokens + output_tokens
                        if total_tokens > 0:
                            self.tracker.track_tokens(total_tokens)
                except Exception:
                    pass
            
            return {
                "response": assistant_message,
                "duration": duration,
                "usage": response.get('usage', {})
            }
        except Exception as e:
            if self.tracker:
                self.tracker.track_duration(time.time() - start_time)
            raise Exception(f"Error invoking Bedrock: {e}")
    
    def _invoke_bedrock_for_config(self, config, tracker, user_message: str) -> Dict[str, Any]:
        """Generic method to invoke Bedrock for any AI Config (chat or judge)."""
        if not config or not config.model:
            return None
        
        # Get system messages and conversation messages from config
        sys_msgs = []
        convo_msgs = []
        
        if config.messages:
            for msg in config.messages:
                if msg.role == "system":
                    sys_msgs.append({"text": msg.content})
                elif msg.role == "user":
                    convo_msgs.append({
                        "role": msg.role,
                        "content": [{"text": msg.content}]
                    })
        
        # Add the current user message (must be last to ensure conversation starts with user)
        convo_msgs.append({
            "role": "user",
            "content": [{"text": user_message}]
        })
        
        # Ensure conversation starts with user message
        if convo_msgs[0]["role"] != "user":
            convo_msgs = [convo_msgs[-1]]
        
        params = {
            "modelId": config.model.name,
            "messages": convo_msgs,
        }
        
        if sys_msgs:
            params["system"] = sys_msgs
        
        # Add any parameters from the model config
        if hasattr(config.model, 'parameters') and config.model.parameters:
            if isinstance(config.model.parameters, dict):
                params.update(config.model.parameters)
        
        start_time = time.time()
        try:
            bedrock_client = get_bedrock_client()
            response = bedrock_client.converse(**params)
            duration = time.time() - start_time
            
            # Extract response
            output = response.get('output', {})
            message = output.get('message', {})
            content = message.get('content', [])
            response_text = content[0].get('text', '') if content else ''
            
            # Track metrics
            if tracker:
                try:
                    tracker.track_duration(duration)
                    usage = response.get('usage', {})
                    if usage and isinstance(usage, dict):
                        input_tokens = usage.get('inputTokens', 0)
                        output_tokens = usage.get('outputTokens', 0)
                        total_tokens = input_tokens + output_tokens
                        if total_tokens > 0:
                            tracker.track_tokens(total_tokens)
                except Exception:
                    pass
            
            return {
                "response": response_text,
                "duration": duration,
                "usage": response.get('usage', {})
            }
        except Exception as e:
            print(f"Error invoking Bedrock: {e}")
            return None
    
    def chat(self, user_message: str) -> str:
        """Process a user message and return the AI response."""
        result = self.invoke_bedrock(user_message)
        return result["response"]
    
    def is_judge_available(self) -> bool:
        """Check if judge is available and enabled."""
        return self.judge_config is not None and self.judge_config.enabled
    
    def chat_with_judge(self, user_message: str) -> Dict[str, Any]:
        """Process a user message, get AI response, and evaluate with judge."""
        # Get the AI response
        result = self.invoke_bedrock(user_message)
        response_text = result["response"]
        
        # Evaluate with judge if available
        judge_result = None
        if self.is_judge_available():
            judge_input = f"Input: {user_message}\n\nOutput: {response_text}"
            judge_result = self._invoke_bedrock_for_config(
                self.judge_config,
                self.judge_tracker,
                judge_input
            )
            if judge_result:
                evaluation_text = judge_result["response"]
                
                # Extract accuracy score from judge response
                # Judge returns text with score embedded like "**Score: 0.0" or "Score: 0.85"
                accuracy_score = None
                try:
                    # First try JSON format
                    parsed = json.loads(evaluation_text)
                    score = parsed.get('score') or parsed.get('accuracy') or parsed.get('accuracy_score')
                    if score is not None:
                        accuracy_score = float(score)
                        if accuracy_score > 1:
                            accuracy_score = accuracy_score / 100.0
                except json.JSONDecodeError:
                    # If not JSON, extract from text using regex
                    # Look for patterns like "Score: 0.85" or "Evaluation Score: 0.0"
                    match = re.search(r'Score:\s*(\d+\.?\d*)', evaluation_text, re.IGNORECASE)
                    if match:
                        accuracy_score = float(match.group(1))
                        # Already normalized (0-1 scale)
                
                # Track accuracy score as event metric to LaunchDarkly
                if accuracy_score is not None:
                    try:
                        ld_client.track('ai-accuracy', self.user_context, None, accuracy_score)
                        ld_client.flush()
                    except Exception:
                        pass
                
                judge_result = {
                    "evaluation": evaluation_text,
                    "accuracy_score": accuracy_score,
                    "usage": judge_result.get("usage", {})
                }
            else:
                judge_result = {"error": "Judge evaluation failed"}
        
        return {
            "response": response_text,
            "judge": judge_result,
            "duration": result.get("duration", 0),
            "usage": result.get("usage", {})
        }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def reset(self):
        """Reset the conversation history."""
        self.conversation_history = []
        if self.config and self.config.messages:
            self.conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in self.config.messages
            ]
    
    def get_model_info(self) -> str:
        """Get the model name/info."""
        if self.config and self.config.model:
            return self.config.model.name
        return "Unknown"

