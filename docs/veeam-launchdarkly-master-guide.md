# Veeam + LaunchDarkly AI Configs Master Guide

This document serves as the master reference for Veeam's integration with LaunchDarkly AI Configs. It covers all supported features, capabilities, and implementation details.

---

## Table of Contents

1. [Overview](#overview)
2. [Tracing & Observability](#tracing--observability)
   - [LLM Observability](#llm-observability)
   - [What LLM Observability Captures](#what-llm-observability-captures)
   - [Setup Requirements](#setup-requirements)
3. [Objective Evaluations](#objective-evaluations)
   - [Online Evals (LLM-as-a-Judge)](#online-evals-llm-as-a-judge)
   - [User Feedback Metrics](#user-feedback-metrics)
   - [Product Analytics Metrics](#product-analytics-metrics)
4. [Inline Evaluation Metrics](#inline-evaluation-metrics)
5. [Experimentation Playground](#experimentation-playground)
   - [LLM Playground](#llm-playground)
6. [AI Configs Overview](#ai-configs-overview)
   - [Completion Mode vs Agent Mode](#completion-mode-vs-agent-mode)
   - [Variations & Targeting](#variations--targeting)
7. [Experiments](#experiments)
   - [A/B Testing Models](#ab-testing-models)
   - [Key Learnings](#key-learnings)
8. [SDK Integration](#sdk-integration)
   - [Python SDK](#python-sdk)
   - [Metrics Tracking](#metrics-tracking)
9. [Known Limitations](#known-limitations)
10. [EU Instance Setup](#eu-instance-setup)
    - [Migration Process](#migration-process)
    - [EU-Specific URLs](#eu-specific-urls)
11. [FedRamp Instance](#fedramp-instance)
12. [References](#references)

---

## Overview

LaunchDarkly AI Configs enables teams to manage AI model configurations outside of application code. This allows:

- Runtime updates to models, prompts, and parameters without redeployment
- Gradual rollouts and A/B testing of AI variations
- Continuous monitoring and evaluation of model performance
- Safe iteration and experimentation with LLMs

---

## Tracing & Observability

### LLM Observability

LaunchDarkly provides LLM observability directly within AI Configs, helping teams connect model behavior to real production outcomes.

> "Traditional observability has always focused on performance metrics: latency, errors, throughput, and cost. But as AI and large language models move into production, those signals alone don't tell the full story. Fast responses can still be wrong, and stable infrastructure can still deliver unpredictable results."
> — [LaunchDarkly Blog](https://launchdarkly.com/blog/llm-observability-in-ai-configs/)

### What LLM Observability Captures

| Metric | Description |
|--------|-------------|
| Prompts | Input text sent to the model |
| Parameters | Temperature, max tokens, etc. |
| Tool calls | Function/tool invocations |
| Responses | Model output text |
| Latency | Time to generate response |
| Token usage | Input/output token counts |
| Cost per call | Estimated cost based on tokens |
| Model version | Provider and model responsible |

### Setup Requirements

1. LaunchDarkly observability SDK
2. OpenLLMetry provider instrumentation
3. Initialize LaunchDarkly SDK **before** OpenLLMetry
4. Policies for handling PII in prompts/responses

**Documentation:** [LLM Observability Docs](https://launchdarkly.com/docs/home/observability/llm-observability)

---

## Objective Evaluations

LaunchDarkly is **agnostic to where metrics come from**. Metrics can originate from:

- Online evals (LLM-as-a-judge)
- User feedback
- Product analytics
- Custom sources

### Online Evals (LLM-as-a-Judge)

Online evals use AI judges to evaluate AI Config outputs in real time. Judges apply consistent evaluation prompts and scoring frameworks.

**Built-in judges:**
- **Accuracy** — evaluates factual correctness
- **Relevance** — assesses relevance to prompts/context
- **Toxicity** — detects harmful/offensive content

Scores appear on the **Monitoring** tab alongside latency, cost, and satisfaction metrics.

**Use cases:**
- Continuously monitor AI quality in production
- Detect regressions after rollouts
- Automate rollbacks/alerts based on evaluation metrics
- Compare prompt/model variations using live data

**Documentation:** [Online Evaluations Docs](https://launchdarkly.com/docs/home/ai-configs/online-evaluations)

### User Feedback Metrics

Track user satisfaction through:
- Thumbs up/down ratings
- Star ratings
- Custom feedback events

### Product Analytics Metrics

Integrate with product analytics to measure:
- Feature adoption
- User engagement
- Business outcomes tied to AI features

---

## Inline Evaluation Metrics

Metrics are automatically captured from your LLM provider and displayed alongside logs or in dashboards:

- Generation count
- Input/output tokens
- Duration
- Time to first token
- Errors/exceptions

These are **passthrough metrics** captured directly from the provider SDK.

---

## Experimentation Playground

### LLM Playground

LaunchDarkly provides an **LLM Playground** where you can:

- Test model prompts before deployment
- Compare different prompt variations
- Experiment with temperature and other parameters
- Preview model responses interactively

**Documentation:** [LLM Playground Docs](https://launchdarkly.com/docs/home/ai-configs/playground#manage-api-keys)

---

## AI Configs Overview

### Completion Mode vs Agent Mode

| Mode | Use Case |
|------|----------|
| **Completion** | Single-step prompts with messages and roles |
| **Agent** | Multi-step workflows with instructions and tools |

### Variations & Targeting

- Create multiple variations (e.g., "strong" vs "fast" model)
- Target variations to specific users, segments, or contexts
- Gradual rollouts with percentage-based allocation

---

## Experiments

### A/B Testing Models

Run experiments to compare:
- Different models (e.g., GPT-4.1 vs GPT-4.1-mini)
- Different prompts
- Different parameters

**Metrics available:**
- Time to first token (average)
- Latency
- Token usage
- Custom metrics

### Key Learnings

1. **Unique context key per request** — use UUID for proper randomization in experiments
2. **CUPED adjustment** — not supported for percentile metrics (p95)
3. **Forcing experiment completion** — LaunchDarkly asks to "ship" a single variation when stopping

---

## SDK Integration

### Python SDK

```python
from ldclient import Context
from ldai.client import LDAIClient, AICompletionConfigDefault

# Initialize LaunchDarkly client
ldclient.set_config(Config(SDK_KEY))
ld_client = ldclient.get()
aiclient = LDAIClient(ld_client)

# Fetch AI Config
config = aiclient.config(
    "chat-assistant-config",
    user_context,
    AICompletionConfigDefault(enabled=False)
)
```

### Metrics Tracking

```python
# Track duration
tracker.track_duration(duration_seconds)

# Track tokens
tracker.track_tokens(total_tokens)
```

---

## Known Limitations

| Limitation | Status | Notes |
|------------|--------|-------|
| Judge evals in Python SDK | ✅ Supported | Was JS-only, now available |
| CUPED for percentile metrics | ❌ Not supported | Use average metrics instead |
| Edit Model Config after creation | ❌ Not supported | Must delete and recreate |
| Unique request ID for experiments | ⚠️ Required | Use UUID per request |

---

## EU Instance Setup

Veeam received approval from security and platform teams to set up a LaunchDarkly instance in the **EU region**.

### Migration Process

The process to migrate from US to EU instance:

1. **Create trial account** in EU instance
2. **Update Salesforce** — change the account ID associated with the account
3. **Shut down old US account**
4. **Account provisioning** — work on the EU instance setup

**Important migration steps:**
- Update SDK keys to point to EU instance
- Update all API endpoints to EU URLs
- Verify billing is pointed to the correct account

### EU-Specific URLs

| Resource | EU URL |
|----------|--------|
| Dashboard | `https://app.eu.launchdarkly.com` |
| API | `https://api.eu.launchdarkly.com` |
| SDK endpoints | See [EU Docs](https://docs.launchdarkly.com/home/getting-started/eu) |

> ⚠️ **Common Issue:** If something isn't working, it's likely because the configuration is not pointing to the EU instance URLs.

**Documentation:** [EU Instance Documentation](https://docs.launchdarkly.com/home/getting-started/eu)

---

## FedRamp Instance

For FedRamp compliance requirements (e.g., VDC FedRamp), a **separate FedRamp instance** is required.

### Next Steps for FedRamp

1. Initiate conversations with LaunchDarkly account team
2. Confirm FedRamp requirements and scope
3. Set up dedicated FedRamp instance
4. Migrate or configure SDK keys for FedRamp environment

*Contact LaunchDarkly account team for FedRamp setup assistance.*

---

## References

### Official Documentation
- [AI Configs Overview](https://launchdarkly.com/docs/home/ai-configs)
- [LLM Observability](https://launchdarkly.com/docs/home/observability/llm-observability)
- [Online Evaluations](https://launchdarkly.com/docs/home/ai-configs/online-evaluations)
- [LLM Playground](https://launchdarkly.com/docs/home/ai-configs/playground)
- [Python AI SDK](https://launchdarkly.com/docs/sdk/ai/python)

### Blog Posts
- [LLM Observability in AI Configs](https://launchdarkly.com/blog/llm-observability-in-ai-configs/)

### Internal Docs
- [App Flow Diagram](./app-flow-diagram.md)
- [File Flow Diagram](./file-flow-diagram.md)
- [Detailed Call Flow](./detailed-call-flow.md)
- [LaunchDarkly Setup Notes](./launchdarkly-setup-notes.md)

---

*Last updated: Feb 2026*
