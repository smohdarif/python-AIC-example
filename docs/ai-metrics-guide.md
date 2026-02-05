# LaunchDarkly AI Metrics Guide

This document explains the metrics automatically tracked by the LaunchDarkly AI SDK and their business value.

## Table of Contents

- [Available Metrics](#available-metrics)
- [How Metrics Are Sent](#how-metrics-are-sent)
- [Business Value](#business-value)
  - [Cost Management](#1-cost-management-)
  - [Performance Monitoring](#2-performance-monitoring-)
  - [Reliability Tracking](#3-reliability-tracking-)
  - [A/B Testing](#4-ab-testing-experiments-)
  - [User Feedback Loop](#5-user-feedback-loop-)
  - [Capacity Planning](#6-capacity-planning-)
- [Real Customer Scenarios](#real-customer-scenarios)
- [Event Data Structure](#event-data-structure)

---

## Available Metrics

| Event Key | Sent When | Value Type |
|-----------|-----------|------------|
| `$ld:ai:duration:total` | `track_duration()` called | Duration in milliseconds |
| `$ld:ai:tokens:total` | `track_tokens()` called | Total token count |
| `$ld:ai:tokens:input` | `track_tokens()` called | Input token count |
| `$ld:ai:tokens:output` | `track_tokens()` called | Output token count |
| `$ld:ai:tokens:ttf` | `track_time_to_first_token()` called | Time to first token (ms) |
| `$ld:ai:generation:success` | `track_success()` called | 1 |
| `$ld:ai:generation:error` | `track_error()` called | 1 |
| `$ld:ai:feedback:user:positive` | `track_feedback(positive)` called | 1 |
| `$ld:ai:feedback:user:negative` | `track_feedback(negative)` called | 1 |

---

## How Metrics Are Sent

**Important**: Metrics are NOT sent automatically. You must explicitly call tracker methods after making AI calls.

```python
from ldai.tracker import TokenUsage

# After a successful AI call
response = bedrock.converse(...)

# Get tracker from config
tracker = getattr(config, 'tracker', None)
if tracker:
    # Track success
    tracker.track_success()
    
    # Track duration (in milliseconds!)
    tracker.track_duration(int(duration * 1000))
    
    # Track tokens using TokenUsage object
    usage = response.get('usage', {})
    tracker.track_tokens(TokenUsage(
        total=usage.get('inputTokens', 0) + usage.get('outputTokens', 0),
        input=usage.get('inputTokens', 0),
        output=usage.get('outputTokens', 0)
    ))

# For Bedrock, there's a convenience method:
tracker.track_bedrock_converse_metrics(response)  # Handles everything
```

### On Error

```python
except Exception as e:
    if tracker:
        tracker.track_error()
        tracker.track_duration(int(duration * 1000))
    raise e
```

---

## Business Value

### 1. Cost Management 💰

| Metric | Use Case |
|--------|----------|
| **Token counts** | Track spend per model/user/feature |
| **Input vs Output tokens** | Optimize prompts (input) vs response length (output) |

**Example**: "GPT-4 is costing $500/day on feature X — switch to Nova Pro and save 60%"

---

### 2. Performance Monitoring ⚡

| Metric | Use Case |
|--------|----------|
| **Completion time (p95/p99)** | Catch slow responses before users complain |
| **Time to first token** | Critical for streaming UX |

**Alert Example**: "p99 latency exceeded 5s — investigate model or prompt issue"

---

### 3. Reliability Tracking 🛡️

| Metric | Use Case |
|--------|----------|
| **Success count** | Track overall health |
| **Error count** | Detect outages, rate limits, model failures |
| **Error rate** | Set SLOs (e.g., 99.5% success) |

**Alert Example**: "Error rate > 5% in last 10 minutes — check AWS Bedrock status"

---

### 4. A/B Testing (Experiments) 🧪

| Scenario | What You Learn |
|----------|----------------|
| **Model A vs Model B** | Which is faster? Cheaper? More accurate? |
| **Prompt v1 vs v2** | Which prompt performs better? |
| **Temperature 0.3 vs 0.7** | Which gives better user satisfaction? |

**Experiment Result Example**: "Claude 3 has 20% lower latency than GPT-4 with same quality"

---

### 5. User Feedback Loop 👍👎

| Metric | Use Case |
|--------|----------|
| **Positive feedback** | Track user satisfaction |
| **Negative feedback** | Identify bad responses for improvement |

**Insight Example**: "Users dislike responses from Variation B — revert to A"

---

### 6. Capacity Planning 📊

| Analysis | Decision |
|----------|----------|
| Token usage trends | When to upgrade rate limits |
| Peak usage times | Scale infrastructure |
| Model popularity | Negotiate better pricing |

---

## Real Customer Scenarios

| Customer Need | LaunchDarkly Solution |
|---------------|----------------------|
| "Our AI costs are unpredictable" | Dashboard showing cost per feature/user |
| "Users complain about slow responses" | P95 latency alerts + model comparison |
| "Which prompt is better?" | A/B test with conversion metrics |
| "Bedrock went down, we didn't know" | Error rate alerts |
| "Prove ROI to leadership" | Usage + success rate dashboards |

---

## Event Data Structure

Example of raw event data sent to LaunchDarkly:

```json
{
  "eventTimeMs": 1770309954000,
  "eventKey": "$ld:ai:tokens:total",
  "eventKind": "custom",
  "value": 24,
  "trackJsonData": {
    "variationKey": "default",
    "configKey": "chat-assistant-config",
    "version": 2,
    "modelName": "amazon.nova-pro-v1:0",
    "providerName": "Bedrock"
  },
  "requestDetail": {
    "application_identifier": "",
    "application_name": "",
    "application_version": "",
    "application_version_name": "",
    "event_source": "backend-sdk",
    "sdk_name": "PythonClient",
    "sdk_version": "9.14.1",
    "user_agent": "PythonClient/9.14.1"
  },
  "contexts": [
    {
      "anonymous": "false",
      "attributes_json": "{\"lastName\":\"Demo\",\"email\":\"user@example.com\",\"firstName\":\"User\"}",
      "context_key": "user-session-123",
      "context_kind": "user"
    }
  ]
}
```

### What This Enables

This rich metadata allows LaunchDarkly to:

- **Track costs** per model/config
- **Compare variations** in experiments
- **Filter dashboards** by user/model/config
- **Alert** on anomalies

---

## Summary

**Without these metrics**: You're flying blind on AI costs, performance, and reliability.

**With these metrics**: You can **optimize cost**, **ensure reliability**, and **prove AI delivers value**.
