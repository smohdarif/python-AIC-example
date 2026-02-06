# AI Configs - Context Quick Start

> **Focus**: Only what you need for LaunchDarkly AI Configs

---

## What is Context?

A **Context** tells LaunchDarkly **who** is making the request. It's used for:
- **Targeting**: Which users get which AI Config variation
- **Prompt Interpolation**: Insert user data into prompts

---

## Basic Context (Most Common)

```python
from ldclient import Context

# Create context for a user
context = Context.builder(user_id) \
    .set("email", user_email) \
    .build()
```

**That's it!** This is enough for most AI Config use cases.

---

## Adding Attributes for Targeting

Add attributes you want to use in targeting rules:

```python
context = Context.builder(user_id) \
    .set("email", "john@example.com") \
    .set("plan", "enterprise")          # Target by subscription
    .set("region", "us-east")           # Target by region
    .set("role", "admin")               # Target by role
    .build()
```

### In LaunchDarkly UI

You can then create targeting rules like:
- `plan` equals `enterprise` → Serve "strong model" variation
- `region` equals `eu-west` → Serve "EU compliant" variation

---

## Prompt Interpolation

Context attributes can be inserted into AI prompts using `{{ldctx.attributeName}}`.

### Example

**Context:**
```python
context = Context.builder("user-123") \
    .set("name", "John") \
    .set("company", "Acme Corp") \
    .set("plan", "enterprise") \
    .build()
```

**System Prompt in LaunchDarkly:**
```
You are a helpful assistant for {{ldctx.company}}.
The user {{ldctx.name}} is on the {{ldctx.plan}} plan.
Provide responses appropriate for their subscription level.
```

**Result (after interpolation):**
```
You are a helpful assistant for Acme Corp.
The user John is on the enterprise plan.
Provide responses appropriate for their subscription level.
```

---

## Multi-Context (User + Organization)

Use when you need to target by **both** user AND organization attributes:

```python
# Create user context
user = Context.builder(user_id) \
    .set("email", "john@acme.com") \
    .set("role", "admin") \
    .build()

# Create organization context
org = Context.builder(org_id) \
    .kind("organization") \
    .set("name", "Acme Corp") \
    .set("plan", "enterprise") \
    .set("industry", "healthcare") \
    .build()

# Combine them
context = Context.multi_builder() \
    .add(user) \
    .add(org) \
    .build()
```

### Interpolation with Multi-Context

```
Hello {{ldctx.user.email}} from {{ldctx.organization.name}}!
Your organization is on the {{ldctx.organization.plan}} plan.
```

---

## Quick Reference

| What You Want | Code |
|---------------|------|
| Simple user context | `Context.builder(user_id).build()` |
| Add email | `.set("email", "user@example.com")` |
| Add custom attribute | `.set("plan", "enterprise")` |
| Build the context | `.build()` |
| Multi-context | `Context.multi_builder().add(user).add(org).build()` |

---

## Common Patterns

### Pattern 1: SaaS Application

```python
context = Context.builder(user_id) \
    .set("email", user_email) \
    .set("plan", "pro")              # free, pro, enterprise
    .set("signup_date", "2024-01-15") \
    .build()
```

**Targeting ideas:**
- Enterprise users → Advanced AI model
- Free users → Basic AI model

---

### Pattern 2: B2B with Organizations

```python
user = Context.builder(user_id) \
    .set("email", user_email) \
    .set("role", user_role) \
    .build()

org = Context.builder(org_id) \
    .kind("organization") \
    .set("plan", org_plan) \
    .set("industry", org_industry) \
    .build()

context = Context.multi_builder().add(user).add(org).build()
```

**Targeting ideas:**
- Healthcare industry → HIPAA-compliant prompts
- Enterprise orgs → Premium model access

---

### Pattern 3: Regional Targeting

```python
context = Context.builder(user_id) \
    .set("email", user_email) \
    .set("region", "eu-west") \
    .set("language", "de") \
    .build()
```

**Targeting ideas:**
- EU region → EU-based model endpoint
- German language → German system prompts

---

## Full Example in Code

```python
from ldclient import Context
from ldai.client import LDAIClient, AICompletionConfigDefault

# 1. Create context
context = Context.builder("user-123") \
    .set("email", "john@acme.com") \
    .set("plan", "enterprise") \
    .build()

# 2. Fetch AI Config (context is used for targeting + interpolation)
fallback = AICompletionConfigDefault(enabled=False)
config = aiclient.completion_config("chat-assistant", context, fallback)

# 3. The config now has:
#    - The variation targeted for this user's "plan"
#    - Prompts with {{ldctx.email}} replaced with "john@acme.com"
```

---

## Checklist

- [ ] User ID is unique and stable (not session-based)
- [ ] Added attributes needed for targeting rules
- [ ] Added attributes needed for prompt interpolation
- [ ] Used `Context.builder()` pattern
- [ ] Called `.build()` at the end

---

*Simple, focused guide for AI Configs context creation.*
