# ⚠️ IMPORTANT: SDK Code Corrections

**Date:** February 2026
**Issue:** The implementation plan documents contain code examples that don't match the official LaunchDarkly AI SDK API

---

## Summary

The documents `LaunchDarkly_AI_Configs_Implementation_Plan.md` and `LaunchDarkly_Implementation_Executive_Summary.md` were created based on general LaunchDarkly documentation patterns, but the **actual Python AI SDK in this repo** has different API patterns.

---

## Key Differences

### 1. Client Initialization

**❌ INCORRECT (in documents):**
```python
from launchdarkly_server_sdk import Context, LDClient
client = LDClient(sdk_key)
ai_config = client.get_ai_config(key, context)
```

**✅ CORRECT (official SDK):**
```python
from ldclient import LDClient, Config, Context
from ldai import LDAIClient

ld_client = LDClient(Config(sdk_key))
ai_client = LDAIClient(ld_client)
```

---

### 2. Getting AI Config

**❌ INCORRECT:**
```python
ai_config = client.get_ai_config("config-key", context)
response = ai_config.execute({"question": question})
```

**✅ CORRECT:**
```python
from ldai import AICompletionConfigDefault, ModelConfig

default_config = AICompletionConfigDefault(
    enabled=True,
    model=ModelConfig(name='claude-3-5-sonnet-20241022')
)

ai_config = ai_client.completion_config(
    "config-key",
    context,
    default_config,
    variables={"question": question}
)

# NO .execute() method - integrate with your LLM provider manually
# OR use the Chat interface (async)
```

---

### 3. Using Chat Interface (Recommended)

**❌ INCORRECT:**
```python
# Synchronous pattern shown in documents
response = ai_config.execute(variables)
```

**✅ CORRECT:**
```python
# Async Chat interface (recommended)
import asyncio

async def main():
    chat = await ai_client.create_chat(
        'config-key',
        context,
        default_config,
        default_ai_provider='bedrock'
    )

    if chat:
        response = await chat.invoke("Your question here")
        print(response.message.content)

asyncio.run(main())
```

---

### 4. Context Creation

**❌ SOMEWHAT INCORRECT:**
```python
# This works but may cause confusion
from launchdarkly_server_sdk import Context
context = Context.builder(user_id).kind("request").build()
```

**✅ CORRECT:**
```python
from ldclient import Context

# Simple
context = Context.create("user-123")

# With attributes
context = Context.builder("user-123") \
    .set("email", "user@example.com") \
    .build()

# For A/B testing - use unique ID
import uuid
context = Context.create(str(uuid.uuid4()))
```

---

### 5. Metrics Tracking

**❌ INCORRECT:**
```python
# Manual tracking shown in documents
client.track("ai-generation", context, data={...})
```

**✅ CORRECT:**
```python
from ldai.tracker import TokenUsage

# Automatic when using Chat
response = await chat.invoke(message)  # Metrics auto-tracked

# Manual tracking
if ai_config.tracker:
    ai_config.tracker.track_success(
        TokenUsage(total=500, input=300, output=200)
    )
```

---

### 6. Default Configuration

**❌ MISSING in documents:**
No mention of required default configuration

**✅ CORRECT:**
```python
from ldai import AICompletionConfigDefault, ModelConfig, LDMessage

# REQUIRED: Must provide default config
default_config = AICompletionConfigDefault(
    enabled=True,
    model=ModelConfig(
        name='claude-3-5-sonnet-20241022',
        parameters={'temperature': 0.7}
    ),
    messages=[
        LDMessage(role='system', content='You are a helpful assistant.')
    ]
)
```

---

## ✅ Use These Resources Instead

### For Correct Code Examples:

1. **SDK_Code_Examples_CORRECTED.md** ⭐ **START HERE**
   - Complete corrected examples
   - Based on official SDK in this repo
   - All patterns verified working

2. **Official SDK Files:**
   - `/python-server-sdk-ai/packages/sdk/server-ai/README.md`
   - `/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/client.py`

3. **Working Examples in This Repo:**
   - `/app.py` - Flask web app
   - `/chat_interaction.py` - Chat implementation

---

## Implementation Plan Documents Status

### ⚠️ Use With Caution:

- `LaunchDarkly_AI_Configs_Implementation_Plan.md` - **Conceptual guide is GOOD, code examples need correction**
- `LaunchDarkly_Implementation_Executive_Summary.md` - **Business case and timeline are GOOD, code examples need correction**

### ✅ These Are Still Valuable:

The implementation plans contain excellent:
- Phase-by-phase approach
- Business justification
- Timeline and resource estimates
- Lessons learned from Veeam
- Risk mitigation strategies
- Success metrics

**Just use `SDK_Code_Examples_CORRECTED.md` for all actual code implementation!**

---

## Quick Migration Guide

If you've already started implementing based on the old examples:

### Step 1: Update Imports
```python
# Change from:
from launchdarkly_server_sdk import LDClient, Context

# To:
from ldclient import LDClient, Config, Context
from ldai import LDAIClient, AICompletionConfigDefault, ModelConfig, LDMessage
```

### Step 2: Update Client Initialization
```python
# Change from:
client = LDClient(sdk_key)

# To:
ld_client = LDClient(Config(sdk_key))
ai_client = LDAIClient(ld_client)
```

### Step 3: Update Config Retrieval
```python
# Change from:
ai_config = client.get_ai_config(key, context)

# To:
default_config = AICompletionConfigDefault(enabled=True, model=ModelConfig(name='model-name'))
ai_config = ai_client.completion_config(key, context, default_config)
```

### Step 4: Update Execution
```python
# Change from:
response = ai_config.execute(variables)

# To:
# Option A: Use Chat (async)
chat = await ai_client.create_chat(key, context, default_config)
response = await chat.invoke(message)

# Option B: Manual integration with LLM provider
# Use ai_config.model, ai_config.messages to call your LLM
# Then track metrics with ai_config.tracker
```

---

## Why This Happened

1. The initial documents were created based on generic LaunchDarkly patterns
2. The Python AI SDK is in alpha and has specific API patterns
3. The SDK uses async/await for Chat interface (best practice)
4. The SDK requires explicit default configurations
5. Integration with LLM providers is more flexible than simple `.execute()`

---

## Action Items

- [ ] Review `SDK_Code_Examples_CORRECTED.md` before starting implementation
- [ ] Update any code already written to use correct patterns
- [ ] Use `/app.py` and `/chat_interaction.py` as reference implementations
- [ ] Refer to official SDK README for latest patterns
- [ ] Consider implementation plans as business/planning guides, not code references

---

**Note to customers:** When working with LaunchDarkly Professional Services, show them the SDK in this repo (`/python-server-sdk-ai/`) and ask them to review code examples against that specific SDK implementation.

---

**Last Updated:** February 2026
**Correction Priority:** HIGH - Use corrected examples before implementing
