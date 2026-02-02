# Document Analysis: Evaluating LaunchDarkly AI Configs for Veeam Intelligence

**Date:** November 5, 2025
**Analyzed:** February 2, 2026

---

## **Key Concepts**

### **AI Model Config**
- Configuration for a specific model deployment
- Includes: endpoint, deployment name, temperature (optional override per use case)
- **Issue:** Azure OpenAI requires custom parameters for endpoint and deployment name, unlike AWS Bedrock which has standardized regional endpoints

### **AI Config**
- Configuration for a specific LLM-based query
- Specifies which AI model config to use
- Defines prompts to feed to the model

---

## **Implementation Details**

### **1. Creating AI Model Configs**
- Created configs for Azure OpenAI Service model deployments
- Separate configs needed for each VDC environment (personal, dev, stage, prod)
- Each Azure OpenAI account has unique endpoint (unlike AWS Bedrock)
- Used Custom Parameters to store: api base endpoint, deployment name, api version
- **Feedback:** Cannot edit Model Configs after creation - must delete and recreate

### **2. Creating AI Configs**
- Created **two "completion-based"** AI configs (not "agent-based"):
  - **Strong model config:** For complex queries (GPT-4.1)
  - **Fast model config:** For simpler queries (GPT-4.1-mini)
- Completion-based vs Agent-based:
  - **Completion:** Single prompt with messages/roles
  - **Agent:** Multi-step workflows with instructions and tools

### **3. SDK Key Setup**
- **Important discovery:** Need SDK key (not API key) to fetch AI configs

### **4. Tracking Metrics**
Added wrapper to track:
- Generation count
- Input tokens
- Output tokens
- Duration
- Time to first token (latency)
- Errors

---

## **Experiments**

### **Primary Experiment:** Time to First Token Comparison
**Goal:** Quantify latency difference between GPT-4.1 vs GPT-4.1-mini

### **Key Issues Encountered:**

1. **Context Kind Problem:**
   - Initially all 100% of requests went to GPT-4.1 (not 50/50 split)
   - Issue: Code wasn't using correct "context kind"
   - Solution: Updated to use "request" context kind

2. **Context Key Problem:**
   - Even with correct context kind, still getting 100% GPT-4.1
   - **Root cause:** Context key was always "anonymous" or same user_id
   - LaunchDarkly hashes context key to determine variation - same key = same variation
   - **Solution:** Generate unique UUID per request using `uuid.uuid4()`
   - Moved user_id from key to attribute for future targeting flexibility

3. **Percentile Metrics Limitation:**
   - Result view and CUPED adjustment don't support percentile analysis (p95)
   - **Workaround:** Recreated experiment with "average time to first token" instead of p95
   - Percentile analysis methods are in beta and not compatible with CUPED adjustments

4. **Experiment Iteration Issue:**
   - Cannot create new iteration if primary metric changes
   - "Primary single metric must match a metric in the metrics list"
   - Had to create entirely new experiment

### **Experiment Results:**
- **115 requests total:** 59 → GPT-4.1, 54 → GPT-4.1-mini
- **Finding:** 62% chance that GPT-4.1-mini is superior for reducing average time to first token

### **Notable Features:**
- Targeting rules auto-update when experiment starts
- Cannot delete/change variations during active experiment (good safeguard)
- "Health check" feature on right side of experiment UI helps validate setup

---

## **Evaluations**

### **Online Evals (AI Judges)**
- AI judges evaluate another AI Config's output in real-time
- Measure: accuracy, relevance, toxicity
- Scores appear on Monitoring tab alongside latency, cost, satisfaction
- Attached all three judges to AI configs

### **Critical Limitation:**
- **Judge evaluation only supported in JavaScript SDK**
- **Problem:** Veeam primarily uses Python and Go for backend AI services
- **Timeline:** Python SDK support estimated by **December 8, 2025** (3 weeks from doc date)

---

## **Other Features Explored**

### **Observability**
- LLM observability features available (marked as TODO in doc)

### **Tracing**
- Marked as TODO in doc

### **Creating Tools**
- LaunchDarkly supports tool orchestration for agent workflows
- **Author's opinion:** "Feels like they're trying to do too much" - applying dynamic configuration to every aspect including agents and tools
- Better suited for dedicated AI agent frameworks, but shows LaunchDarkly has pulse on AI/agentic trends

---

## **POC Code**
- Pull request available: https://github.com/veeam-ai/veeam-intelligence/pull/742 (restricted content)
- Integrates AI configs into Veeam Intelligence for VDC

---

## **Analysis Section**
- Marked as "TODO Zack" - pending completion

---

## **Key Takeaways**

### **Pros:**
1. Strong experimentation platform with automatic traffic allocation
2. Good metrics tracking and observability
3. Health checks provide confidence in experiment setup
4. Opinionated design forces decisiveness (e.g., must ship a variation when stopping experiment)
5. Automatic targeting rule updates when experiments start
6. Protection against result contamination (can't modify variations during active experiments)

### **Cons/Limitations:**
1. Azure OpenAI requires custom parameters vs standardized AWS Bedrock approach
2. Cannot edit Model Configs after creation
3. Percentile metrics (p95) don't support CUPED adjustments (in beta)
4. Judge evaluations only in JS SDK currently (Python coming soon)
5. Context key management requires careful implementation for proper randomization
6. Tool orchestration may be overreach for LaunchDarkly's core competency
7. Cannot iterate experiments if primary metric changes

### **Critical Implementation Detail:**
For proper A/B testing, **must use unique request IDs** as context keys, otherwise traffic won't randomize correctly across variations.

---

## **Technical Debugging Insights**

### **The Context Key Issue (Most Important Learning):**
```python
# WRONG - This won't randomize properly
context = Context.builder("anonymous").kind("request").build()

# CORRECT - Unique key per request for proper randomization
import uuid
context = Context.builder(str(uuid.uuid4())).kind("request").set("user_id", user_id).build()
```

**Why this matters:**
- LaunchDarkly uses the context key for hashing to determine which variation to serve
- Same key = same hash = same variation every time
- Unique keys allow proper traffic distribution across experiment variations
- User-specific data can be preserved as attributes for future targeting

---

## **Open Questions/TODOs**
1. Test dynamic prompts with placeholder values in AI config prompt
2. Complete comprehensive analysis (assigned to Zack)
3. Explore LLM observability features in depth
4. Test tracing capabilities
5. Evaluate whether agent-based configs provide value for Veeam Intelligence workflows

---

## **Recommendations**

1. **For Production Use:**
   - Implement unique request ID generation for all AI config evaluations
   - Wait for Python SDK judge evaluation support before relying on online evals
   - Use average metrics instead of percentile metrics for experiments until CUPED support is added

2. **Feature Requests to LaunchDarkly:**
   - Enable editing of Model Configs after creation
   - Support percentile metrics with CUPED adjustments
   - Consider making endpoint/deployment name first-class parameters for Azure OpenAI

3. **Architecture Decisions:**
   - Use completion-based configs for Veeam Intelligence (appropriate for current workflow)
   - Consider agent-based configs only if multi-step reasoning becomes a requirement
   - Evaluate dedicated AI agent frameworks for complex tool orchestration rather than relying on LaunchDarkly

---

## **References**
- Original document: `Veeam_Evaluating Launch Darkly AI Configs - Arif'sCopy.md`
- Original PDF: `Veeam_Evaluating Launch Darkly AI Configs - Arif'sCopy.pdf`
- LaunchDarkly Documentation: Various links referenced throughout original document
- Azure OpenAI Configuration documentation referenced
