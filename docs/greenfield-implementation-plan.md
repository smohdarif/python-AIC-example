# LaunchDarkly AI Configs - Greenfield Implementation Plan

## Executive Summary

A phased approach to implementing LaunchDarkly AI Configs for your organization, enabling dynamic AI model management, observability, and experimentation.

---

## Phase 1: Foundation (Week 1-2)

| Activity | Owner | Deliverable |
|----------|-------|-------------|
| **EU Instance Setup** | LD PS + Customer | Configured LD EU instance |
| **Project/Environment Structure** | LD PS | Dev, Staging, Prod environments |
| **SDK Integration** | Customer Dev Team | Python/Node SDK installed in app |
| **AWS Bedrock/OpenAI Credentials** | Customer | AI provider access configured |
| **First AI Config** | LD PS + Customer | "Hello World" config working |

**Success Criteria**: Single AI Config returning responses in Dev environment

---

## Phase 2: Core Implementation (Week 3-4)

| Activity | Owner | Deliverable |
|----------|-------|-------------|
| **AI Model Configs** | Customer + LD PS | Model definitions (costs, params) |
| **System Prompts** | Customer | Production prompts in LD |
| **Context/Targeting Setup** | LD PS | User attributes for targeting |
| **Metrics Instrumentation** | Customer Dev | Token, latency, success tracking |
| **Basic Dashboard** | LD PS | Observability metrics visible |

**Success Criteria**: Production-ready AI Config with metrics flowing

---

## Phase 3: Observability & Optimization (Week 5-6)

| Activity | Owner | Deliverable |
|----------|-------|-------------|
| **LLM Observability Dashboard** | LD PS | Cost, latency, error dashboards |
| **Alerting Rules** | Customer + LD | Error rate, latency alerts |
| **Cost Tracking** | LD PS | Per-model, per-feature cost view |
| **Performance Baselines** | Customer | p95/p99 latency benchmarks |

**Success Criteria**: Full visibility into AI operations

---

## Phase 4: Advanced Features (Week 7-8)

| Activity | Owner | Deliverable |
|----------|-------|-------------|
| **A/B Testing Setup** | LD PS | First model/prompt experiment |
| **Targeting Rules** | Customer + LD | User segmentation (beta users, regions) |
| **LLM Judge (Optional)** | LD PS | Automated response evaluation |
| **Rollout Strategy** | LD PS | Progressive rollout playbook |

**Success Criteria**: Running first A/B test on AI Config

---

## Phase 5: Production Rollout (Week 9-10)

| Activity | Owner | Deliverable |
|----------|-------|-------------|
| **Staging Validation** | Customer QA | All configs tested |
| **Production Deployment** | Customer + LD | AI Configs live in Prod |
| **Runbook Creation** | LD PS | Incident response procedures |
| **Team Training** | LD PS | Engineering team enabled |
| **Handoff** | LD PS | Customer self-sufficient |

**Success Criteria**: Production live, team trained, LD PS disengaged

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Customer Application                         │
├─────────────────────────────────────────────────────────────────┤
│  LaunchDarkly SDK (Python/Node)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ AI Config   │  │ Targeting   │  │ Metrics     │             │
│  │ (prompts,   │  │ (who gets   │  │ (tokens,    │             │
│  │  model)     │  │  what)      │  │  latency)   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│              LaunchDarkly EU Instance                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ AI Configs  │  │ Experiments │  │ Dashboards  │             │
│  │ Library     │  │ & Rollouts  │  │ & Alerts    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              AI Provider (Customer-Owned)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ AWS Bedrock │  │ OpenAI      │  │ Azure AI    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Decisions Needed from Customer

| Question | Options | Impact |
|----------|---------|--------|
| **AI Provider** | AWS Bedrock / OpenAI / Azure | SDK integration approach |
| **Models to use** | GPT-4, Claude, Nova Pro, etc. | Cost & performance |
| **Number of AI features** | 1-5 / 5-20 / 20+ | Config structure |
| **User targeting needs** | None / Basic / Advanced | Context setup complexity |
| **Experimentation goals** | None / Model comparison / Prompt testing | Phase 4 scope |

---

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Foundation | 2 weeks | Week 2 |
| Core Implementation | 2 weeks | Week 4 |
| Observability | 2 weeks | Week 6 |
| Advanced Features | 2 weeks | Week 8 |
| Production Rollout | 2 weeks | Week 10 |

**Total: ~10 weeks** (can be compressed for simpler use cases)

---

## Investment Required

| Resource | Customer | LaunchDarkly PS |
|----------|----------|-----------------|
| **Engineering** | 1-2 developers (part-time) | PS Engineer |
| **Product/AI** | AI/ML team input on prompts | — |
| **DevOps** | CI/CD pipeline access | — |
| **Time** | 4-6 hrs/week | 8-12 hrs/week |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to first AI Config | < 1 week |
| Metrics visibility | 100% of AI calls tracked |
| Mean time to prompt change | < 5 minutes (vs hours with code deploy) |
| A/B test capability | Running within 8 weeks |

---

## Next Steps

1. ✅ EU Instance configured
2. ⏳ **Schedule kickoff with LD Professional Services**
3. ⏳ Customer identifies first AI use case
4. ⏳ Begin Phase 1

---

## Appendix: EU Instance Specifics

### EU URLs
- **App**: `https://app.launchdarkly.eu`
- **SDK Base URI**: `https://sdk.launchdarkly.eu`
- **Stream URI**: `https://stream.launchdarkly.eu`
- **Events URI**: `https://events.launchdarkly.eu`

### SDK Configuration for EU

```python
from ldclient.config import Config

config = Config(
    sdk_key="your-sdk-key",
    base_uri="https://sdk.launchdarkly.eu",
    stream_uri="https://stream.launchdarkly.eu",
    events_uri="https://events.launchdarkly.eu"
)
```

---

*Document prepared for customer onboarding to LaunchDarkly AI Configs*
