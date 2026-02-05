# Coding Guidelines for LaunchDarkly AI Configs

**Repository:** python-AIC-example
**Last Updated:** February 2026
**Status:** MANDATORY for all contributors

---

## 🔴 PRIMARY RULE: Official SDK Reference

### **ALL code examples, documentation, and implementations MUST use patterns from the official Python AI SDK in this repository.**

**Official SDK Location:**
```
/python-server-sdk-ai/packages/sdk/server-ai/
```

**Official SDK Documentation:**
```
/python-server-sdk-ai/packages/sdk/server-ai/README.md
```

**Official SDK Source:**
```
/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/
```

---

## ✅ Verified Reference Implementations

### When writing code or examples, ALWAYS reference these files:

1. **Official SDK README** (Primary)
   - `/python-server-sdk-ai/packages/sdk/server-ai/README.md`
   - Contains official API patterns
   - Shows correct initialization and usage

2. **Official SDK Client** (Primary)
   - `/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/client.py`
   - Contains actual method signatures
   - Shows correct parameter names and types

3. **Working Application Examples** (Reference)
   - `/app.py` - Flask web application
   - `/chat_interaction.py` - Chat implementation
   - Verified working implementations

4. **Corrected Documentation** (Reference)
   - `/docs/SDK_Code_Examples_CORRECTED.md` - Comprehensive examples
   - `/docs/IMPORTANT_SDK_CORRECTIONS.md` - Common mistakes to avoid

---

## ❌ DO NOT Reference

### These sources should NOT be used for code examples:

- Generic LaunchDarkly documentation (may not match Python SDK)
- Implementation plan documents (business/planning only)
- Online tutorials not specific to this SDK version
- Code examples from other LaunchDarkly SDKs (JS, Go, etc.)
- ChatGPT or AI-generated code not verified against official SDK

---

## 📋 Mandatory Patterns

### 1. Client Initialization

**✅ CORRECT:**
```python
from ldclient import LDClient, Config, Context
from ldai import LDAIClient

ld_client = LDClient(Config(sdk_key))
ai_client = LDAIClient(ld_client)
```

**❌ INCORRECT:**
```python
from launchdarkly_server_sdk import LDClient
client = LDClient(sdk_key)
```

### 2. Getting AI Config

**✅ CORRECT:**
```python
from ldai import AICompletionConfigDefault, ModelConfig, LDMessage

default_config = AICompletionConfigDefault(
    enabled=True,
    model=ModelConfig(name='model-name'),
    messages=[LDMessage(role='system', content='System prompt')]
)

ai_config = ai_client.completion_config(
    'config-key',
    context,
    default_config,
    variables={'key': 'value'}
)
```

**❌ INCORRECT:**
```python
ai_config = client.get_ai_config('config-key', context)
response = ai_config.execute({'key': 'value'})
```

### 3. Using Chat Interface (Recommended)

**✅ CORRECT:**
```python
import asyncio

async def main():
    chat = await ai_client.create_chat(
        'config-key',
        context,
        default_config,
        default_ai_provider='bedrock'
    )

    if chat:
        response = await chat.invoke(message)
        print(response.message.content)

asyncio.run(main())
```

**❌ INCORRECT:**
```python
# Synchronous pattern not supported
response = ai_config.execute(variables)
```

### 4. Context Creation

**✅ CORRECT:**
```python
from ldclient import Context
import uuid

# Simple
context = Context.create("user-123")

# With attributes
context = Context.builder("user-123") \
    .set("email", "user@example.com") \
    .build()

# For A/B testing - MUST use unique ID
context = Context.create(str(uuid.uuid4()))
```

**❌ INCORRECT:**
```python
from launchdarkly_server_sdk import Context
context = Context.builder("anonymous").kind("request").build()
```

### 5. Import Statements

**✅ CORRECT:**
```python
from ldclient import LDClient, Config, Context
from ldai import (
    LDAIClient,
    AICompletionConfigDefault,
    AIJudgeConfigDefault,
    ModelConfig,
    LDMessage,
    ProviderConfig
)
from ldai.tracker import TokenUsage
```

**❌ INCORRECT:**
```python
from launchdarkly_server_sdk import Context, LDClient
from launchdarkly_server_sdk.integrations import AIConfig
```

---

## 🔍 Verification Process

### Before committing any code:

1. **Check Method Names:**
   - Search in `/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/client.py`
   - Verify method exists with exact signature

2. **Check Import Paths:**
   - Verify imports work from `ldclient` and `ldai`
   - Test imports in Python REPL

3. **Check Parameters:**
   - Verify parameter names match official SDK
   - Check if parameters are required or optional
   - Verify parameter types

4. **Test Against Working Examples:**
   - Compare with `/app.py` or `/chat_interaction.py`
   - Ensure pattern is consistent

5. **Verify Async/Sync:**
   - Check if method is async (needs `await`)
   - Use `asyncio.run()` for async code in examples

---

## 📝 Documentation Standards

### When creating documentation:

1. **Always include this disclaimer:**
   ```markdown
   **Code examples verified against:**
   - Official SDK: `/python-server-sdk-ai/packages/sdk/server-ai/`
   - SDK Version: [version from SDK]
   - Last Verified: [date]
   ```

2. **Reference official files:**
   ```markdown
   See official SDK documentation:
   - README: `/python-server-sdk-ai/packages/sdk/server-ai/README.md`
   - Client API: `/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/client.py`
   ```

3. **Link to working examples:**
   ```markdown
   Working example: See `/app.py` lines XX-YY
   ```

4. **Show wrong vs. right:**
   ```markdown
   ❌ INCORRECT:
   [show wrong pattern]

   ✅ CORRECT:
   [show right pattern from official SDK]
   ```

---

## 🚨 Common Mistakes to Avoid

### Based on previous errors in this repo:

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|------------------|
| Using `client.get_ai_config()` | Method doesn't exist | Use `ai_client.completion_config()` |
| Using `ai_config.execute()` | Method doesn't exist | Use Chat interface or manual integration |
| Importing from `launchdarkly_server_sdk` | Wrong package | Import from `ldclient` and `ldai` |
| No default configuration | SDK requires it | Always provide `AICompletionConfigDefault` |
| Synchronous patterns | SDK uses async for Chat | Use `async`/`await` with `asyncio` |
| Static context keys in experiments | Breaks randomization | Use `str(uuid.uuid4())` |

See `/docs/IMPORTANT_SDK_CORRECTIONS.md` for full list.

---

## 🔄 Update Process

### When SDK is updated:

1. **Check for API changes:**
   ```bash
   cd python-server-sdk-ai/packages/sdk/server-ai
   git log --oneline -10
   cat CHANGELOG.md
   ```

2. **Update working examples:**
   - Test `/app.py`
   - Test `/chat_interaction.py`
   - Fix any breaking changes

3. **Update documentation:**
   - Update `/docs/SDK_Code_Examples_CORRECTED.md`
   - Update version numbers
   - Update "Last Verified" dates

4. **Test all examples:**
   - Run examples in clean environment
   - Verify imports work
   - Check for deprecation warnings

---

## 🤖 For AI Assistants (Claude, etc.)

### When generating code for this repository:

1. **ALWAYS read these files FIRST:**
   ```
   /python-server-sdk-ai/packages/sdk/server-ai/README.md
   /python-server-sdk-ai/packages/sdk/server-ai/src/ldai/client.py
   /docs/SDK_Code_Examples_CORRECTED.md
   ```

2. **NEVER generate code without:**
   - Checking method names in official SDK
   - Verifying import paths
   - Confirming async/sync patterns
   - Checking against working examples

3. **If unsure:**
   - Read the official SDK source code
   - Check working examples (`app.py`, `chat_interaction.py`)
   - Ask user to verify against SDK
   - Add disclaimer that verification is needed

4. **For documentation:**
   - Always include reference to official SDK
   - Show where pattern was verified
   - Link to specific files and line numbers

---

## ✅ Pre-Commit Checklist

Before committing code or documentation:

- [ ] Code verified against official SDK in `/python-server-sdk-ai/`
- [ ] Imports tested and working
- [ ] Method names match official SDK
- [ ] Parameters match official SDK signatures
- [ ] Async/await used correctly
- [ ] Compared with working examples (`app.py`, `chat_interaction.py`)
- [ ] No patterns from generic LaunchDarkly docs
- [ ] Documentation includes verification statement
- [ ] References to official SDK files included
- [ ] Tested in clean Python environment
- [ ] No deprecated methods used

---

## 📞 Questions?

If you're unsure about a pattern:

1. Check official SDK source: `/python-server-sdk-ai/packages/sdk/server-ai/src/ldai/`
2. Check working examples: `/app.py`, `/chat_interaction.py`
3. Check corrected docs: `/docs/SDK_Code_Examples_CORRECTED.md`
4. Search SDK for method: `grep -r "method_name" python-server-sdk-ai/`
5. Ask in commit message for review

**When in doubt, reference the official SDK first!**

---

## 📚 Additional Resources

### In This Repository:

- `/docs/README.md` - Documentation navigation
- `/docs/SDK_Code_Examples_CORRECTED.md` - Verified examples
- `/docs/IMPORTANT_SDK_CORRECTIONS.md` - Common mistakes
- `/app.py` - Working Flask application
- `/chat_interaction.py` - Working chat implementation

### Official LaunchDarkly:

- Python AI SDK: https://github.com/launchdarkly/python-server-sdk-ai
- Documentation: https://docs.launchdarkly.com/sdk/ai/python
- Support: support@launchdarkly.com

---

## 🔐 Enforcement

**This guideline is MANDATORY for:**

- All code commits
- All documentation updates
- All examples and tutorials
- All AI-generated code
- All external contributions

**Violations will result in:**

- PR rejection
- Request for corrections
- Rewrite based on official SDK

**No exceptions** - accuracy and consistency are critical for customer implementations.

---

**Version:** 1.0
**Last Updated:** February 2026
**Maintainer:** Arif Shaikh, AI Practice Lead
**Status:** ACTIVE - MANDATORY COMPLIANCE
