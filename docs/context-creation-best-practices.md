# Context Creation Best Practices

> **Source**: All examples are from the official LaunchDarkly Python SDK  
> **Reference**: `python-server-sdk/ldclient/context.py` and `python-server-sdk-ai/` tests

---

## Table of Contents

- [What is a Context?](#what-is-a-context)
- [Basic Context Creation](#basic-context-creation)
- [Builder Pattern (Recommended)](#builder-pattern-recommended)
- [Setting Custom Attributes](#setting-custom-attributes)
- [Multi-Context (Multiple Kinds)](#multi-context-multiple-kinds)
- [Context Interpolation in AI Configs](#context-interpolation-in-ai-configs)
- [Private Attributes](#private-attributes)
- [Anonymous Contexts](#anonymous-contexts)
- [Best Practices Summary](#best-practices-summary)
- [Common Patterns for AI Configs](#common-patterns-for-ai-configs)

---

## What is a Context?

A **Context** is a collection of attributes that LaunchDarkly uses for:
- **Targeting**: Decide which users/entities get which variation
- **Analytics**: Track usage by user segments
- **Interpolation**: Insert context values into AI prompts

```python
from ldclient import Context
```

---

## Basic Context Creation

### Simple Context (Key Only)

```python
# From SDK: Context.create(key, kind)
# Kind defaults to "user" if not specified

# Simplest form - just a key
context = Context.create("user-123")

# With explicit kind
context = Context.create("user-123", "user")
context = Context.create("org-456", "organization")
context = Context.create("device-789", "device")
```

**When to use**: When you only need the key for targeting and don't need additional attributes.

---

## Builder Pattern (Recommended)

The builder pattern is recommended for creating contexts with multiple attributes.

### Basic Builder

```python
# From SDK tests: test_model_config.py
context = Context.builder('user-key').name("Sandy").build()
```

### Builder with Multiple Attributes

```python
# From SDK tests: test_model_config.py
context = Context.builder('user-key') \
    .name("Sandy") \
    .set('last', 'Beaches') \
    .build()
```

### Builder with Kind

```python
# From SDK: context.py
context = Context.builder('org-key') \
    .kind('org') \
    .name("LaunchDarkly") \
    .set('shortname', 'LD') \
    .build()
```

---

## Setting Custom Attributes

### Available Attribute Types

```python
# From SDK: context.py - attribute types are JSON-compatible
context = Context.builder('user-key') \
    .set('plan', 'enterprise')           # String
    .set('age', 25)                       # Number
    .set('is_admin', True)                # Boolean
    .set('tags', ['premium', 'beta'])     # Array/List
    .set('preferences', {                 # Object/Dict
        'theme': 'dark',
        'language': 'en'
    }) \
    .build()
```

### Built-in String Attributes

```python
# From SDK: context.py line 13
# These are pre-defined string attributes:
_USER_STRING_ATTRS = {'name', 'firstName', 'lastName', 'email', 'country', 'avatar', 'ip'}

# Example usage
context = Context.builder('user-123') \
    .name('John Doe') \
    .set('firstName', 'John') \
    .set('lastName', 'Doe') \
    .set('email', 'john@example.com') \
    .set('country', 'US') \
    .build()
```

---

## Multi-Context (Multiple Kinds)

Multi-contexts allow targeting based on multiple entity types simultaneously.

### Using create_multi()

```python
# From SDK: context.py
user_context = Context.create('user-123', 'user')
org_context = Context.create('org-456', 'organization')

multi_context = Context.create_multi(user_context, org_context)
```

### Using multi_builder()

```python
# From SDK tests: test_model_config.py and test_agents.py
user_context = Context.builder('user-key') \
    .name("Sandy") \
    .build()

org_context = Context.builder('org-key') \
    .kind('org') \
    .name("LaunchDarkly") \
    .set('shortname', 'LD') \
    .build()

# Build multi-context
context = Context.multi_builder() \
    .add(user_context) \
    .add(org_context) \
    .build()
```

### Multi-Context with More Attributes

```python
# From SDK tests: test_agents.py
user_context = Context.builder('user-key') \
    .name('Alice') \
    .build()

org_context = Context.builder('org-key') \
    .kind('org') \
    .name('LaunchDarkly') \
    .set('tier', 'Enterprise') \
    .build()

context = Context.multi_builder() \
    .add(user_context) \
    .add(org_context) \
    .build()
```

---

## Context Interpolation in AI Configs

Context attributes can be interpolated into AI prompts using `{{ldctx.attributeName}}` syntax.

### Single Context Interpolation

```python
# From SDK tests: test_model_config.py
# AI Config prompt: "Hello {{ldctx.name}}, your last name is {{ldctx.last}}"

context = Context.builder('user-key') \
    .name("Sandy") \
    .set('last', 'Beaches') \
    .build()

# When fetching AI Config, the prompt becomes:
# "Hello Sandy, your last name is Beaches"
```

### Multi-Context Interpolation

```python
# From SDK tests: test_model_config.py
# AI Config prompt: "Hello {{ldctx.user.name}} from {{ldctx.org.name}} ({{ldctx.org.shortname}})"

user_context = Context.builder('user-key') \
    .name("Sandy") \
    .build()

org_context = Context.builder('org-key') \
    .kind('org') \
    .name("LaunchDarkly") \
    .set('shortname', 'LD') \
    .build()

context = Context.multi_builder() \
    .add(user_context) \
    .add(org_context) \
    .build()

# When fetching AI Config, the prompt becomes:
# "Hello Sandy from LaunchDarkly (LD)"
```

### Agent Context Interpolation

```python
# From SDK tests: test_agents.py
# For AI Agents with expertise-based routing

context = Context.builder('user-key') \
    .set('expertise', 'advanced') \
    .build()

# AI Config can reference: {{ldctx.expertise}}
```

---

## Private Attributes

Private attributes are NOT sent to LaunchDarkly events/analytics but CAN be used for targeting.

```python
# From SDK tests: test_context.py
context = Context.builder('user-key') \
    .set('email', 'user@example.com') \
    .set('ssn', '123-45-6789') \
    .private('email', 'ssn') \
    .build()

# email and ssn will:
# ✅ Be used for flag targeting
# ❌ NOT appear in LaunchDarkly analytics/dashboard
```

### Private Nested Attributes

```python
# From SDK: context.py
# Can mark nested properties as private using slash-delimited paths

context = Context.builder('user-key') \
    .set('address', {
        'street': '123 Main St',
        'city': 'Boston',
        'zip': '02101'
    }) \
    .private('/address/street', '/address/zip') \
    .build()

# Only street and zip are private, city is still visible
```

---

## Anonymous Contexts

Anonymous contexts are used for entities you don't want indexed in the LaunchDarkly dashboard.

```python
# From SDK tests: test_context.py
context = Context.builder('session-abc123') \
    .anonymous(True) \
    .build()

# This context:
# ✅ Can be used for flag evaluations
# ❌ Won't appear in the Contexts list in dashboard
# ✅ Still included in analytics events
```

**Use cases**:
- Temporary sessions
- Pre-login users
- High-volume automated systems
- Testing/development

---

## Best Practices Summary

### 1. Always Use Builder Pattern for Multiple Attributes

```python
# ✅ GOOD
context = Context.builder('user-123') \
    .name('John') \
    .set('email', 'john@example.com') \
    .set('plan', 'enterprise') \
    .build()

# ❌ AVOID - Only use for simple cases
context = Context.create('user-123')
```

### 2. Use Meaningful Keys

```python
# ✅ GOOD - Unique, stable identifiers
context = Context.builder('user-uuid-abc123').build()
context = Context.builder('org-id-456').kind('org').build()

# ❌ BAD - Non-unique or unstable
context = Context.builder('John').build()  # Names aren't unique
context = Context.builder('session-temp').build()  # Temporary IDs
```

### 3. Use Appropriate Kinds

```python
# ✅ GOOD - Semantic kinds
Context.builder('user-123').kind('user').build()
Context.builder('org-456').kind('organization').build()
Context.builder('device-789').kind('device').build()
Context.builder('service-abc').kind('service').build()

# Kind naming rules:
# - Only letters, numbers, '.', '_', '-'
# - Cannot be "kind" or "multi"
# - Case-sensitive
```

### 4. Mark Sensitive Data as Private

```python
# ✅ GOOD - PII is private
context = Context.builder('user-123') \
    .set('email', 'user@example.com') \
    .set('phone', '+1234567890') \
    .private('email', 'phone') \
    .build()
```

### 5. Use Multi-Context for Complex Targeting

```python
# ✅ GOOD - When you need to target by user AND organization
user = Context.builder('user-123').name('John').build()
org = Context.builder('org-456').kind('org').set('plan', 'enterprise').build()
context = Context.multi_builder().add(user).add(org).build()

# Now you can target:
# - All users in enterprise orgs
# - Specific users regardless of org
# - Specific orgs regardless of user
```

---

## Common Patterns for AI Configs

### Pattern 1: User Context for Personalization

```python
# For personalizing AI responses

context = Context.builder(user_id) \
    .name(user_name) \
    .set('email', user_email) \
    .set('plan', subscription_plan)      # For targeting by plan
    .set('language', preferred_language) # For prompt localization
    .set('expertise', user_expertise)    # For response complexity
    .build()

# AI Config prompt can use:
# "You are helping {{ldctx.name}}, a {{ldctx.expertise}} user..."
```

### Pattern 2: Organization Context for B2B

```python
# For B2B applications with org-level features

user = Context.builder(user_id) \
    .name(user_name) \
    .set('role', user_role) \
    .build()

org = Context.builder(org_id) \
    .kind('organization') \
    .name(org_name) \
    .set('plan', org_plan)           # enterprise, pro, free
    .set('industry', org_industry)   # For industry-specific prompts
    .set('size', employee_count)     # For capacity-based features
    .build()

context = Context.multi_builder().add(user).add(org).build()

# Target rules:
# - "enterprise" orgs get advanced model
# - "healthcare" industry gets HIPAA-compliant prompts
```

### Pattern 3: Device/Session Context

```python
# For device-specific AI behavior

user = Context.builder(user_id).name(user_name).build()

device = Context.builder(device_id) \
    .kind('device') \
    .set('type', 'mobile')           # mobile, desktop, tablet
    .set('os', 'iOS') \
    .set('app_version', '2.1.0') \
    .build()

context = Context.multi_builder().add(user).add(device).build()

# Target rules:
# - Mobile users get shorter responses
# - Old app versions get fallback behavior
```

### Pattern 4: A/B Testing Context

```python
# For running experiments

context = Context.builder(user_id) \
    .name(user_name) \
    .set('experiment_cohort', 'treatment_a')  # or 'control'
    .set('signup_date', '2024-01-15') \
    .set('user_segment', 'power_user') \
    .build()

# Target rules:
# - 50% of users get new prompt (treatment)
# - 50% get existing prompt (control)
```

---

## Quick Reference

| Method | Purpose | Example |
|--------|---------|---------|
| `Context.create(key)` | Simple context | `Context.create('user-123')` |
| `Context.builder(key)` | Builder pattern | `Context.builder('user-123').name('John').build()` |
| `.kind(kind)` | Set context kind | `.kind('organization')` |
| `.name(name)` | Set display name | `.name('John Doe')` |
| `.set(attr, value)` | Set custom attribute | `.set('plan', 'enterprise')` |
| `.anonymous(True)` | Mark as anonymous | `.anonymous(True)` |
| `.private(*attrs)` | Mark attrs as private | `.private('email', 'phone')` |
| `Context.multi_builder()` | Multi-context builder | See examples above |

---

*Document created from official LaunchDarkly Python SDK source code.*
