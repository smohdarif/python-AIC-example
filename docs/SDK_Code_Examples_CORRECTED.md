# LaunchDarkly AI SDK - Corrected Code Examples

**Based on:** Official `launchdarkly-server-sdk-ai` Python SDK in this repo
**Date:** February 2026

---

## Installation

```bash
# Install both SDKs
pip install launchdarkly-server-sdk
pip install launchdarkly-server-sdk-ai

# For AWS Bedrock
pip install boto3

# For environment variables
pip install python-dotenv
```

---

## Basic Setup

```python
import os
from dotenv import load_dotenv
from ldclient import LDClient, Config, Context
from ldai import LDAIClient, AICompletionConfigDefault, ModelConfig, LDMessage

# Load environment variables
load_dotenv()

# Initialize LaunchDarkly client
LD_SDK_KEY = os.getenv("LAUNCHDARKLY_SDK_KEY")
ld_client = LDClient(Config(LD_SDK_KEY))

# Initialize AI client
ai_client = LDAIClient(ld_client)
```

---

## Creating Context

```python
# Simple context
context = Context.create("user-123")

# Context with attributes
context = Context.builder("user-123") \
    .set("firstName", "John") \
    .set("lastName", "Smith") \
    .set("email", "john.smith@example.com") \
    .set("tier", "premium") \
    .build()

# For A/B testing - CRITICAL: Use unique ID per request
import uuid
context = Context.create(str(uuid.uuid4()))
```

---

## Getting AI Config (Synchronous)

```python
from ldai import AICompletionConfigDefault, ModelConfig, LDMessage

# Create default config (fallback if LD is unavailable)
default_config = AICompletionConfigDefault(
    enabled=True,
    model=ModelConfig(
        name='claude-3-5-sonnet-20241022',
        parameters={'temperature': 0.7, 'maxTokens': 1000}
    ),
    messages=[
        LDMessage(role='system', content='You are a helpful assistant.')
    ]
)

# Get AI config from LaunchDarkly
ai_config = ai_client.completion_config(
    'customer-support-assistant',  # AI Config key in LD
    context,
    default_config,
    variables={'customerName': 'John'}  # Optional: for template interpolation
)

# Check if enabled
if ai_config.enabled:
    model_name = ai_config.model.name
    messages = ai_config.messages
    tracker = ai_config.tracker
    # Use with your LLM provider
```

---

## Using Chat Interface (Async - Recommended)

```python
import asyncio
from ldai import LDAIClient, AICompletionConfigDefault, ModelConfig, LDMessage

async def main():
    # Create AI client
    ai_client = LDAIClient(ld_client)

    # Create default config
    default_config = AICompletionConfigDefault(
        enabled=True,
        model=ModelConfig(name='claude-3-5-sonnet-20241022'),
        messages=[
            LDMessage(role='system', content='You are a helpful assistant.')
        ]
    )

    # Create context
    context = Context.create("user-123")

    # Create chat instance
    chat = await ai_client.create_chat(
        'customer-support-chat',
        context,
        default_config,
        variables={'customerName': 'John'},
        default_ai_provider='bedrock'  # or 'openai', 'anthropic', etc.
    )

    if chat:
        # Simple conversation - metrics automatically tracked
        response1 = await chat.invoke('I need help with my order')
        print(response1.message.content)

        # Follow-up question - history maintained
        response2 = await chat.invoke("What's the status?")
        print(response2.message.content)

        # Access conversation history
        messages = chat.get_messages()
        print(f'Conversation has {len(messages)} messages')

asyncio.run(main())
```

---

## Manual LLM Integration (AWS Bedrock Example)

```python
import boto3
import json

def call_bedrock_with_ld_config(ai_config, user_message: str):
    """Call AWS Bedrock using LaunchDarkly AI Config."""

    if not ai_config.enabled:
        raise Exception("AI Config is disabled")

    # Get model info from config
    model_id = ai_config.model.name
    temperature = ai_config.model.get_parameter('temperature', 0.7)
    max_tokens = ai_config.model.get_parameter('maxTokens', 1000)

    # Build conversation history
    messages = []
    if ai_config.messages:
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in ai_config.messages
        ]
    messages.append({"role": "user", "content": user_message})

    # Call AWS Bedrock
    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body)
    )

    response_body = json.loads(response['body'].read())

    # Track metrics
    if ai_config.tracker:
        ai_config.tracker.track_success(
            TokenUsage(
                total=response_body.get('usage', {}).get('total_tokens', 0),
                input=response_body.get('usage', {}).get('input_tokens', 0),
                output=response_body.get('usage', {}).get('output_tokens', 0)
            )
        )

    return response_body['content'][0]['text']

# Usage
context = Context.create("user-123")
ai_config = ai_client.completion_config(
    'customer-support-assistant',
    context,
    default_config
)

response = call_bedrock_with_ld_config(ai_config, "How do I reset my password?")
print(response)
```

---

## Metrics Tracking

```python
from ldai.tracker import TokenUsage

# Metrics are automatically tracked when using chat.invoke()
# For manual tracking:

if ai_config.tracker:
    # Track successful completion
    ai_config.tracker.track_success(
        TokenUsage(
            total=500,
            input=300,
            output=200
        )
    )

    # Track failure
    ai_config.tracker.track_failure(
        TokenUsage(total=0, input=0, output=0),
        "Error message here"
    )
```

---

## A/B Testing Example

```python
import uuid
import asyncio

async def run_ab_test():
    """Run A/B test comparing two models."""

    # CRITICAL: Use unique request ID for proper randomization
    request_id = str(uuid.uuid4())
    context = Context.create(request_id)

    # Get AI config (LaunchDarkly will assign variation)
    default_config = AICompletionConfigDefault(
        enabled=True,
        model=ModelConfig(name='claude-3-5-sonnet-20241022')
    )

    chat = await ai_client.create_chat(
        'experiment-config',
        context,
        default_config,
        default_ai_provider='bedrock'
    )

    if chat:
        # This request participates in the experiment
        response = await chat.invoke("What is machine learning?")
        print(f"Model: {chat.get_model_info()}")
        print(f"Response: {response.message.content}")

        # Metrics automatically tracked by LaunchDarkly

asyncio.run(run_ab_test())
```

---

## Smart Routing (Fast vs Strong Model)

```python
class SmartRouter:
    def __init__(self, ai_client, fast_config_key, strong_config_key):
        self.ai_client = ai_client
        self.fast_config_key = fast_config_key
        self.strong_config_key = strong_config_key

    def is_complex_query(self, question: str) -> bool:
        """Determine if query needs strong model."""
        complex_keywords = ['explain', 'why', 'how does', 'compare', 'analyze']
        return any(keyword in question.lower() for keyword in complex_keywords) \
            or len(question.split()) > 15

    async def route_query(self, user_id: str, question: str) -> str:
        """Route query to appropriate model."""
        context = Context.create(user_id)

        # Choose config based on complexity
        config_key = self.strong_config_key if self.is_complex_query(question) \
            else self.fast_config_key

        default_config = AICompletionConfigDefault(
            enabled=True,
            model=ModelConfig(name='claude-3-5-sonnet-20241022')
        )

        # Create chat
        chat = await self.ai_client.create_chat(
            config_key,
            context,
            default_config,
            default_ai_provider='bedrock'
        )

        if chat:
            response = await chat.invoke(question)
            return response.message.content

        return "Error: Unable to process request"

# Usage
router = SmartRouter(ai_client, 'fast-assistant', 'strong-assistant')
response = asyncio.run(router.route_query("user-123", "Explain quantum computing"))
```

---

## Dynamic Prompts with Variables

```python
# In LaunchDarkly UI, create prompt with variables:
# System: "You are a {{tone}} assistant for {{company_name}}"
# User: "Customer: {{customer_name}}\nQuestion: {{question}}"

context = Context.create("user-123")
default_config = AICompletionConfigDefault(
    enabled=True,
    model=ModelConfig(name='claude-3-5-sonnet-20241022'),
    messages=[
        LDMessage(role='system', content='You are a helpful assistant.')
    ]
)

# Pass variables for interpolation
ai_config = ai_client.completion_config(
    'customer-support-assistant',
    context,
    default_config,
    variables={
        'tone': 'professional',
        'company_name': 'Acme Corp',
        'customer_name': 'John Smith',
        'question': 'How do I reset my password?'
    }
)

# Variables are interpolated in the messages
print(ai_config.messages[0].content)
# Output: "You are a professional assistant for Acme Corp"
```

---

## Environment-Based Targeting

```python
# Create context with environment attribute
context = Context.builder(str(uuid.uuid4())) \
    .set("environment", "production") \
    .set("tier", "premium") \
    .build()

# In LaunchDarkly UI, create targeting rules:
# IF environment == "development" THEN use Haiku (fast, cheap)
# IF environment == "staging" THEN use Sonnet (balanced)
# IF environment == "production" AND tier == "premium" THEN use Opus (best)

ai_config = ai_client.completion_config(
    'environment-aware-assistant',
    context,
    default_config
)

# LaunchDarkly serves appropriate model based on targeting rules
```

---

## Judge Evaluation (AI Quality Assessment)

```python
from ldai import AIJudgeConfigDefault

async def evaluate_with_judge():
    """Use AI judge to evaluate response quality."""

    context = Context.create("user-123")

    # Create judge config
    judge_default = AIJudgeConfigDefault(
        enabled=True,
        model=ModelConfig(name='claude-3-5-sonnet-20241022'),
        evaluation_metric_key='$ld:ai:judge:relevance',
        messages=[
            LDMessage(
                role='system',
                content='Evaluate if the AI response answers the user question. Score 1-5.'
            )
        ]
    )

    # Create judge
    judge = await ai_client.create_judge(
        'relevance-judge',
        context,
        judge_default,
        default_ai_provider='bedrock'
    )

    if judge:
        # Evaluate a response
        result = await judge.evaluate(
            "What is the capital of France?",
            "The capital of France is Paris."
        )

        if result and result.evals:
            relevance_eval = result.evals.get('$ld:ai:judge:relevance')
            if relevance_eval:
                print(f'Relevance score: {relevance_eval.score}')
                print(f'Reasoning: {relevance_eval.reasoning}')

asyncio.run(evaluate_with_judge())
```

---

## Complete Example: Customer Support Chatbot

```python
import os
import asyncio
import uuid
from ldclient import LDClient, Config, Context
from ldai import LDAIClient, AICompletionConfigDefault, ModelConfig, LDMessage

class CustomerSupportBot:
    def __init__(self, sdk_key: str):
        ld_client = LDClient(Config(sdk_key))
        self.ai_client = LDAIClient(ld_client)
        self.chat_sessions = {}

    async def create_session(self, user_id: str) -> str:
        """Create new chat session."""
        session_id = str(uuid.uuid4())

        context = Context.builder(user_id) \
            .set("session_id", session_id) \
            .build()

        default_config = AICompletionConfigDefault(
            enabled=True,
            model=ModelConfig(name='claude-3-5-sonnet-20241022'),
            messages=[
                LDMessage(
                    role='system',
                    content='You are a helpful customer support assistant.'
                )
            ]
        )

        chat = await self.ai_client.create_chat(
            'customer-support-chat',
            context,
            default_config,
            default_ai_provider='bedrock'
        )

        if chat:
            self.chat_sessions[session_id] = chat
            return session_id

        raise Exception("Failed to create chat session")

    async def send_message(self, session_id: str, message: str) -> str:
        """Send message and get response."""
        chat = self.chat_sessions.get(session_id)
        if not chat:
            raise Exception(f"Session {session_id} not found")

        response = await chat.invoke(message)
        return response.message.content

    def get_history(self, session_id: str) -> list:
        """Get conversation history."""
        chat = self.chat_sessions.get(session_id)
        if not chat:
            return []

        return [
            {"role": msg.role, "content": msg.content}
            for msg in chat.get_messages()
        ]

# Usage
async def main():
    bot = CustomerSupportBot(os.getenv("LAUNCHDARKLY_SDK_KEY"))

    # Create session
    session_id = await bot.create_session("user-123")
    print(f"Session created: {session_id}")

    # Chat
    response1 = await bot.send_message(session_id, "How do I reset my password?")
    print(f"Bot: {response1}")

    response2 = await bot.send_message(session_id, "Where do I find my account settings?")
    print(f"Bot: {response2}")

    # Get history
    history = bot.get_history(session_id)
    print(f"Conversation has {len(history)} messages")

asyncio.run(main())
```

---

## Key Differences from Documentation Examples

### ❌ INCORRECT (Old/Generic Examples):
```python
# Don't use these patterns
client.get_ai_config()  # Wrong method name
response = ai_config.execute()  # No execute method
context = Context.builder("anonymous")  # Bad for A/B testing
```

### ✅ CORRECT (Official SDK):
```python
# Use these patterns
ai_client.completion_config()  # Correct method
chat = await ai_client.create_chat()  # Use Chat interface
response = await chat.invoke()  # Invoke on chat object
context = Context.create(str(uuid.uuid4()))  # Unique ID for experiments
```

---

## Reference Files

- **Official SDK:** `/python-server-sdk-ai/packages/sdk/server-ai/`
- **README:** `/python-server-sdk-ai/packages/sdk/server-ai/README.md`
- **Client:** `/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/client.py`
- **Example App:** `/app.py`
- **Chat Example:** `/chat_interaction.py`

---

**Last Updated:** February 2026
**SDK Version:** launchdarkly-server-sdk-ai (alpha)
