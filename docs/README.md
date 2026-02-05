# LaunchDarkly AI Configs Documentation

**Comprehensive guides for implementing LaunchDarkly AI Configs with Python**

---

## 📖 Coding Guidelines

**⚠️ MANDATORY:** All code must follow patterns from the official Python AI SDK in this repo.

See: [`/CODING_GUIDELINES.md`](../CODING_GUIDELINES.md)

**Key Rule:** Always reference `/python-server-sdk-ai/` for code examples. Never use generic LaunchDarkly patterns.

---

## 🚨 START HERE

### For Implementation (Code):
**📘 [SDK_Code_Examples_CORRECTED.md](SDK_Code_Examples_CORRECTED.md)** ⭐ **USE THIS FOR ALL CODE**
- Verified against official Python AI SDK in this repo
- Complete working examples
- All patterns tested and correct

### For Planning (Business):
**📗 [LaunchDarkly_Implementation_Executive_Summary.md](LaunchDarkly_Implementation_Executive_Summary.md)**
- High-level overview for stakeholders
- Business case and ROI
- Timeline and resources
- ⚠️ Ignore code examples in this doc - use SDK_Code_Examples_CORRECTED.md instead

**📕 [LaunchDarkly_AI_Configs_Implementation_Plan.md](LaunchDarkly_AI_Configs_Implementation_Plan.md)**
- Detailed 8-10 week implementation guide
- Phase-by-phase approach
- Lessons from Veeam
- ⚠️ Ignore code examples in this doc - use SDK_Code_Examples_CORRECTED.md instead

---

## ⚠️ Important Notice

**Read This First:** [IMPORTANT_SDK_CORRECTIONS.md](IMPORTANT_SDK_CORRECTIONS.md)

The implementation plan documents contain code examples that don't match the official SDK API. Always use `SDK_Code_Examples_CORRECTED.md` for actual code implementation.

---

## Document Guide

### Implementation & Code

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **SDK_Code_Examples_CORRECTED.md** ⭐ | Correct code examples | **Always - for all coding** |
| IMPORTANT_SDK_CORRECTIONS.md | Explains differences | Before starting implementation |
| LaunchDarkly_AI_Configs_Tutorial.md | Hands-on tutorial | Learning the platform |

### Planning & Strategy

| Document | Purpose | When to Use |
|----------|---------|-------------|
| LaunchDarkly_Implementation_Executive_Summary.md | Executive overview | Customer presentations |
| LaunchDarkly_AI_Configs_Implementation_Plan.md | Detailed plan | Project execution |
| Veeam_LaunchDarkly_AI_Configs_Analysis.md | Production learnings | Understanding gotchas |

### Reference Materials

| Document | Purpose | When to Use |
|----------|---------|-------------|
| COPY_PASTE_PROMPT.txt | Org chart modification | Specific use case only |
| SIMPLE_THREE_OPTIONS_VERIFIED.txt | Career path options | Specific use case only |
| Image modification prompts | Org chart editing | Specific use case only |

---

## Quick Start

### 1. For New Implementation

```bash
# Read in this order:
1. IMPORTANT_SDK_CORRECTIONS.md        # Understand what's different
2. SDK_Code_Examples_CORRECTED.md      # Learn correct patterns
3. LaunchDarkly_Implementation_Executive_Summary.md  # Business context
4. LaunchDarkly_AI_Configs_Implementation_Plan.md    # Detailed planning
```

### 2. For Customer Presentation

```bash
# Present in this order:
1. LaunchDarkly_Implementation_Executive_Summary.md  # High-level (30 min)
2. LaunchDarkly_AI_Configs_Implementation_Plan.md   # Deep-dive (60 min)
3. SDK_Code_Examples_CORRECTED.md                   # Technical demo
```

### 3. For Actual Coding

```bash
# Only use these:
1. SDK_Code_Examples_CORRECTED.md      # Primary reference
2. /app.py                             # Working example
3. /chat_interaction.py                # Working example
4. /python-server-sdk-ai/              # Official SDK
```

---

## File Structure

```
docs/
├── README.md (this file)
│
├── ⭐ PRIORITY FILES (Code Implementation)
│   ├── SDK_Code_Examples_CORRECTED.md ⭐ PRIMARY CODE REFERENCE
│   ├── IMPORTANT_SDK_CORRECTIONS.md
│   └── LaunchDarkly_AI_Configs_Tutorial.md
│
├── 📋 PLANNING FILES (Business & Strategy)
│   ├── LaunchDarkly_Implementation_Executive_Summary.md
│   ├── LaunchDarkly_AI_Configs_Implementation_Plan.md
│   └── Veeam_LaunchDarkly_AI_Configs_Analysis.md
│
└── 🎨 SPECIFIC USE CASES (Org Charts, Career Paths)
    ├── COPY_PASTE_PROMPT.txt
    ├── SIMPLE_THREE_OPTIONS_VERIFIED.txt
    ├── FINAL_Image_Edit_Prompt.md
    ├── Image_Modification_Prompt_For_Org_Chart.md
    ├── Quick_Prompt_For_Image_Edit.txt
    ├── SINGLE_IMAGE_ALL_THREE_OPTIONS.txt
    ├── OPTION_1_STANDALONE.txt
    └── THREE_SEPARATE_OPTIONS_PROMPTS.md
```

---

## Common Questions

### Q: Which document has the correct Python code?
**A:** `SDK_Code_Examples_CORRECTED.md` - This is the ONLY document with verified code examples.

### Q: Can I use code from the implementation plan?
**A:** No. Use it for planning/business case only. All code should come from `SDK_Code_Examples_CORRECTED.md`.

### Q: What's wrong with the code in the implementation plan?
**A:** It uses generic patterns that don't match the actual Python AI SDK. See `IMPORTANT_SDK_CORRECTIONS.md` for details.

### Q: I already started coding from the implementation plan. What do I do?
**A:** Read the migration guide in `IMPORTANT_SDK_CORRECTIONS.md` and update your code.

### Q: Is the business case and timeline still valid?
**A:** Yes! The planning, timeline, ROI, and strategy are all still correct. Just don't use the code examples.

### Q: Where can I find working examples?
**A:** Three places:
1. `SDK_Code_Examples_CORRECTED.md` (comprehensive)
2. `/app.py` (Flask web app)
3. `/chat_interaction.py` (chat implementation)

---

## Key Learnings

### From Veeam Implementation:

1. **Context Keys Must Be Unique for A/B Testing** ⚠️ CRITICAL
   ```python
   # ❌ Wrong
   context = Context.create("user-123")

   # ✅ Correct for experiments
   context = Context.create(str(uuid.uuid4()))
   ```

2. **Use Async Chat Interface** (Recommended)
   ```python
   chat = await ai_client.create_chat(key, context, default_config)
   response = await chat.invoke(message)
   ```

3. **Always Provide Default Config**
   ```python
   default_config = AICompletionConfigDefault(
       enabled=True,
       model=ModelConfig(name='model-name')
   )
   ```

4. **Model Configs Cannot Be Edited**
   - Plan carefully before creation
   - Must delete and recreate to change

5. **Use Average Metrics for Experiments**
   - Percentile (p95) doesn't support CUPED adjustments
   - Stick with average metrics

---

## Next Steps

1. ✅ Read `IMPORTANT_SDK_CORRECTIONS.md`
2. ✅ Review `SDK_Code_Examples_CORRECTED.md`
3. ✅ Look at `/app.py` and `/chat_interaction.py`
4. ✅ Read Executive Summary for business context
5. ✅ Use Implementation Plan for project timeline
6. ✅ Schedule LaunchDarkly PS consultation

---

## Support

**Repository Examples:**
- `/app.py` - Flask application
- `/chat_interaction.py` - Chat implementation
- `/python-server-sdk-ai/` - Official SDK source

**LaunchDarkly Resources:**
- Docs: https://docs.launchdarkly.com/sdk/ai/python
- Support: support@launchdarkly.com

---

**Last Updated:** February 2026
**Maintained by:** Arif Shaikh, AI Practice Lead
