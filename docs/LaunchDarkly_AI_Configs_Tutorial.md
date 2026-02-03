# LaunchDarkly AI Configs Tutorial with AWS Bedrock

**Purpose:** Progressive hands-on tutorial for LaunchDarkly AI Configs using AWS Bedrock
**Target Audience:** Developers learning LD AI Configs for client implementations
**Based on:** Veeam Intelligence LaunchDarkly evaluation

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Use Case 0: Environment Setup](#use-case-0-environment-setup)
3. [Use Case 1: Basic AI Config - Simple Completion](#use-case-1-basic-ai-config---simple-completion)
4. [Use Case 2: Multiple Model Configs - Fast vs Strong](#use-case-2-multiple-model-configs---fast-vs-strong)
5. [Use Case 3: Tracking Metrics](#use-case-3-tracking-metrics)
6. [Use Case 4: A/B Testing with Experiments](#use-case-4-ab-testing-with-experiments)
7. [Use Case 5: Dynamic Prompts with Variables](#use-case-5-dynamic-prompts-with-variables)
8. [Use Case 6: Environment-Based Targeting](#use-case-6-environment-based-targeting)
9. [Use Case 7: Online Evaluations (AI Judges)](#use-case-7-online-evaluations-ai-judges)
10. [Troubleshooting Guide](#troubleshooting-guide)

---

## Prerequisites

### What You Need:
- LaunchDarkly account (free trial available)
- AWS account with Bedrock access
- Python 3.8+ or Node.js 16+
- Basic understanding of AI/LLM concepts

### AWS Bedrock Models Available:
- **Claude 3.5 Sonnet** - Strong model for complex tasks
- **Claude 3.5 Haiku** - Fast model for simple tasks
- **Claude 3 Opus** - Most capable model
- Check your region for model availability

### Key Concepts Recap:

**AI Model Config:**
- Configuration for a specific model deployment
- For AWS Bedrock: Region is the main parameter (endpoints are standardized)
- Simpler than Azure OpenAI (no custom endpoint needed)

**AI Config:**
- Configuration for a specific LLM query/workflow
- References an AI Model Config
- Contains prompts and settings

### Python Client Architecture:

This tutorial uses **3 clients** that work together:

```
┌────────────────────────────────────────────────────────────┐
│  1. LD Client (ldclient)     →  Connects to LaunchDarkly   │
│         ↓                                                   │
│  2. AI Client (LDAIClient)   →  Fetches AI Configs         │
│         ↓                                                   │
│  3. Bedrock Client (boto3)   →  Calls AWS AI models        │
└────────────────────────────────────────────────────────────┘
```

> **See Also:** [Clients & Context Flow](./clients-and-context-flow.md) for detailed diagrams

---

## Use Case 0: Environment Setup

### Step 1: Get Your LaunchDarkly SDK Key

1. Log into LaunchDarkly dashboard
2. Navigate to: **Account Settings** → **Projects** → Select your project
3. Go to **Environments** tab
4. Find your environment (e.g., "Test")
5. Click **SDK key** dropdown
6. Copy the **SDK key** (NOT the API key)

### Step 2: Set Up Environment Variables

```bash
# .env file
LAUNCHDARKLY_SDK_KEY=sdk-xxxxx-xxxxx-xxxxx
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Step 3: Install Dependencies

**For Python:**
```bash
pip install launchdarkly-server-sdk launchdarkly-server-sdk-ai boto3 python-dotenv flask flask-cors
```

> **Note:** You need BOTH `launchdarkly-server-sdk` (core SDK) AND `launchdarkly-server-sdk-ai` (AI extension)

**For Node.js:**
```bash
npm install @launchdarkly/node-server-sdk @aws-sdk/client-bedrock-runtime dotenv
```

### Step 4: Verify AWS Bedrock Access

**Python:**
```python
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)

# List available models
response = bedrock.list_foundation_models()
print("Available Bedrock models:")
for model in response['modelSummaries']:
    print(f"  - {model['modelId']}")
```

---

## Use Case 1: Basic AI Config - Simple Completion

**Goal:** Create your first AI Config and get a simple completion
**Complexity:** ⭐ Beginner
**Time:** 15 minutes

### Step 1: Create AI Model Config in LaunchDarkly UI

1. Go to **AI Configs** → **Models** → **Add model**
2. Fill in:
   - **Name:** `claude-sonnet-bedrock`
   - **Provider:** AWS Bedrock
   - **Model ID:** Select "Claude 3.5 Sonnet"
   - **Input token cost:** 0.003 (per 1K tokens)
   - **Output token cost:** 0.015 (per 1K tokens)
3. Click **Save**

**Note:** Unlike Azure, AWS Bedrock uses standardized endpoints per region, so no custom parameters needed!

### Step 2: Create AI Config in LaunchDarkly UI

1. Go to **AI Configs** → **Create AI Config**
2. Select **Completion-based** (not Agent-based)
3. Fill in:
   - **Name:** `simple-question-answering`
   - **Maintainer:** Your name
4. Click **Create**

### Step 3: Configure the AI Config

1. Under **Model configuration**, select `claude-sonnet-bedrock`
2. Under **Messages**, add a System prompt:
   ```
   You are a helpful assistant that answers questions concisely.
   ```
3. Add a User prompt:
   ```
   {{user_question}}
   ```
4. Set **Max tokens:** 500
5. Set **Temperature:** 0.7
6. Click **Save changes**

### Step 4: Test with Code

**Python:**
```python
import os
import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai.client import LDAIClient, AICompletionConfigDefault
from dotenv import load_dotenv

load_dotenv()

# Step 1: Initialize LaunchDarkly client
ldclient.set_config(Config(os.getenv('LAUNCHDARKLY_SDK_KEY')))
ld_client = ldclient.get()

# Step 2: Create AI Client (wraps LD client)
aiclient = LDAIClient(ld_client)

# Step 3: Create a context (identifies WHO is making the request)
context = Context.builder("user-123") \
    .set("email", "user@example.com") \
    .build()

# Step 4: Fetch AI Config from LaunchDarkly
config_key = "chat-assistant-config"
fallback = AICompletionConfigDefault(enabled=False)
config = aiclient.config(config_key, context, fallback)

if not config.enabled:
    print("AI Config is disabled")
    exit(1)

# Step 5: Build messages from config
system_messages = [
    {"text": msg.content}
    for msg in config.messages
    if msg.role == "system"
]
conversation = [
    {"role": "user", "content": [{"text": "What is the capital of France?"}]}
]

# Step 6: Call AWS Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
response = bedrock.converse(
    modelId=config.model.name,
    system=system_messages,
    messages=conversation
)

# Step 7: Extract and print response
output = response['output']['message']['content'][0]['text']
print("AI Response:")
print(output)

# Track metrics (optional)
tracker = getattr(config, 'tracker', None)
if tracker:
    tracker.track_tokens(response['usage']['inputTokens'] + response['usage']['outputTokens'])
```

**Expected Output:**
```
AI Response:
The capital of France is Paris.
```

### Step 5: Verify in LaunchDarkly Dashboard

1. Go to **AI Configs** → Select `simple-question-answering`
2. Click **Monitoring** tab
3. You should see:
   - Generation count: 1
   - Input/output token counts
   - Average duration

---

## Use Case 2: Multiple Model Configs - Fast vs Strong

**Goal:** Create two AI Configs for different model tiers
**Complexity:** ⭐⭐ Beginner-Intermediate
**Time:** 20 minutes
**Builds on:** Use Case 1

### Why Two Configs?

- **Fast model (Haiku):** Simple queries, lower cost, faster response
- **Strong model (Sonnet):** Complex queries, higher quality, slower response

### Step 1: Create Second AI Model Config

1. Go to **AI Configs** → **Models** → **Add model**
2. Fill in:
   - **Name:** `claude-haiku-bedrock`
   - **Provider:** AWS Bedrock
   - **Model ID:** Select "Claude 3.5 Haiku"
   - **Input token cost:** 0.0008 (per 1K tokens)
   - **Output token cost:** 0.004 (per 1K tokens)
3. Click **Save**

### Step 2: Create Two AI Configs

**Config 1: Fast Query Handler**
1. Create new AI Config: `fast-query-handler`
2. Select model: `claude-haiku-bedrock`
3. System prompt:
   ```
   You are a quick assistant that answers simple questions in one sentence.
   ```
4. User prompt:
   ```
   {{question}}
   ```
5. Max tokens: 100, Temperature: 0.5

**Config 2: Complex Query Handler**
1. Create new AI Config: `complex-query-handler`
2. Select model: `claude-sonnet-bedrock`
3. System prompt:
   ```
   You are an expert assistant that provides detailed, well-reasoned answers to complex questions.
   Include examples and explanations when relevant.
   ```
4. User prompt:
   ```
   {{question}}
   ```
5. Max tokens: 1000, Temperature: 0.7

### Step 3: Create Query Router

**Python:**
```python
import os
import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai.client import LDAIClient, AICompletionConfigDefault
from dotenv import load_dotenv

load_dotenv()

# Initialize clients once at module level
ldclient.set_config(Config(os.getenv('LAUNCHDARKLY_SDK_KEY')))
ld_client = ldclient.get()
aiclient = LDAIClient(ld_client)
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

class QueryRouter:
    def __init__(self):
        pass  # Clients initialized at module level

    def is_complex_query(self, question):
        """Simple heuristic to determine query complexity"""
        complex_keywords = ['explain', 'why', 'how does', 'compare', 'analyze', 'detailed']
        question_lower = question.lower()

        # Check for complex keywords
        if any(keyword in question_lower for keyword in complex_keywords):
            return True

        # Check for length (longer questions often need detailed answers)
        if len(question.split()) > 10:
            return True

        return False

    def route_query(self, question, user_id="anonymous"):
        """Route query to appropriate AI Config"""
        # Create context
        context = Context.builder(user_id).build()

        # Determine which config to use
        if self.is_complex_query(question):
            config_key = "complex-query-handler"
            print(f"🧠 Routing to STRONG model (complex query)")
        else:
            config_key = "fast-query-handler"
            print(f"⚡ Routing to FAST model (simple query)")

        # Get AI Config from LaunchDarkly
        fallback = AICompletionConfigDefault(enabled=False)
        config = aiclient.config(config_key, context, fallback)

        if not config.enabled:
            return "AI Config is disabled"

        # Build messages
        system_msgs = [{"text": msg.content} for msg in config.messages if msg.role == "system"]
        messages = [{"role": "user", "content": [{"text": question}]}]

        # Call Bedrock
        response = bedrock.converse(
            modelId=config.model.name,
            system=system_msgs,
            messages=messages
        )

        return response['output']['message']['content'][0]['text']

# Test the router
if __name__ == "__main__":
    router = QueryRouter()

    # Test simple query
    simple_q = "What is 2+2?"
    print(f"\nQ: {simple_q}")
    print(f"A: {router.route_query(simple_q)}\n")

    # Test complex query
    complex_q = "Explain how machine learning differs from traditional programming"
    print(f"Q: {complex_q}")
    print(f"A: {router.route_query(complex_q)}\n")

    router.close()
```

### Expected Output:
```
⚡ Routing to FAST model (simple query)
Q: What is 2+2?
A: 2+2 equals 4.

🧠 Routing to STRONG model (complex query)
Q: Explain how machine learning differs from traditional programming
A: Machine learning differs from traditional programming in that instead of explicitly
coding rules and logic, ML systems learn patterns from data. Traditional programming
requires developers to anticipate and code every scenario, while ML models discover
patterns through training on examples...
```

---

## Use Case 3: Tracking Metrics

**Goal:** Track and monitor AI Config performance metrics
**Complexity:** ⭐⭐ Intermediate
**Time:** 25 minutes
**Builds on:** Use Case 2

### Key Metrics to Track:
1. **Generation count** - Total successful completions
2. **Input tokens** - Cost tracking
3. **Output tokens** - Cost tracking
4. **Duration** - Total time to generate
5. **Time to first token** - Latency metric (TTFT)
6. **Errors** - Failed generations
7. **Cost** - Calculated from tokens

### Step 1: Create Metrics Wrapper

**Python:**
```python
import os
import time
import uuid
from datetime import datetime
import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai.client import LDAIClient, AICompletionConfigDefault
from dotenv import load_dotenv

load_dotenv()

# Initialize clients once
ldclient.set_config(Config(os.getenv('LAUNCHDARKLY_SDK_KEY')))
ld_client = ldclient.get()
aiclient = LDAIClient(ld_client)
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

class MetricsTracker:
    def __init__(self):
        self.metrics = []

    def track_completion(self, config_key, question, user_id=None):
        """Execute AI Config with full metrics tracking"""
        # Generate unique request ID for proper randomization
        request_id = str(uuid.uuid4())

        # Create context
        resolved_user_id = user_id or request_id
        context = Context.builder(resolved_user_id).build()

        # Track start time
        start_time = time.time()

        try:
            # Get AI Config from LaunchDarkly
            fallback = AICompletionConfigDefault(enabled=False)
            config = aiclient.config(config_key, context, fallback)

            if not config.enabled:
                raise Exception("AI Config is disabled")

            # Build messages
            system_msgs = [{"text": msg.content} for msg in config.messages if msg.role == "system"]
            messages = [{"role": "user", "content": [{"text": question}]}]

            # Call Bedrock
            response = bedrock.converse(
                modelId=config.model.name,
                system=system_msgs,
                messages=messages
            )

            # Calculate duration
            end_time = time.time()
            duration = end_time - start_time

            # Extract metrics from response
            usage = response.get('usage', {})
            metrics = {
                "request_id": request_id,
                "config_key": config_key,
                "timestamp": datetime.utcnow().isoformat(),
                "question": question,
                "answer": response['output']['message']['content'][0]['text'],
                "input_tokens": usage.get('inputTokens', 0),
                "output_tokens": usage.get('outputTokens', 0),
                "total_tokens": usage.get('inputTokens', 0) + usage.get('outputTokens', 0),
                "duration_ms": duration * 1000,
                "model": config.model.name,
                "success": True,
                "error": None
            }

            # Track metrics via LaunchDarkly tracker
            tracker = getattr(config, 'tracker', None)
            if tracker:
                tracker.track_duration(duration)
                tracker.track_tokens(metrics["total_tokens"])

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            metrics = {
                "request_id": request_id,
                "config_key": config_key,
                "timestamp": datetime.utcnow().isoformat(),
                "question": question,
                "answer": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "duration_ms": duration * 1000,
                "model": None,
                "success": False,
                "error": str(e)
            }

        self.metrics.append(metrics)
        return metrics

    def get_summary(self):
        """Get summary statistics"""
        if not self.metrics:
            return "No metrics collected yet"

        successful = [m for m in self.metrics if m['success']]
        failed = [m for m in self.metrics if not m['success']]

        total_input_tokens = sum(m['input_tokens'] for m in successful)
        total_output_tokens = sum(m['output_tokens'] for m in successful)
        avg_duration = sum(m['duration_ms'] for m in successful) / len(successful) if successful else 0

        # Estimate cost (example rates for Bedrock Claude)
        input_cost = (total_input_tokens / 1000) * 0.003
        output_cost = (total_output_tokens / 1000) * 0.015
        total_cost = input_cost + output_cost

        summary = f"""
📊 METRICS SUMMARY
{'='*50}
Total Requests: {len(self.metrics)}
✅ Successful: {len(successful)}
❌ Failed: {len(failed)}

Token Usage:
  Input tokens: {total_input_tokens:,}
  Output tokens: {total_output_tokens:,}
  Total tokens: {total_input_tokens + total_output_tokens:,}

Performance:
  Avg duration: {avg_duration:.2f} ms

💰 Estimated Cost:
  Input cost: ${input_cost:.4f}
  Output cost: ${output_cost:.4f}
  Total cost: ${total_cost:.4f}
"""
        return summary

# Test metrics tracking
if __name__ == "__main__":
    tracker = MetricsTracker()

    # Run multiple queries
    questions = [
        "What is the capital of France?",
        "Explain quantum computing",
        "What is 5 times 7?",
        "How does photosynthesis work?",
        "What year did World War 2 end?"
    ]

    for question in questions:
        print(f"\n🤔 Question: {question}")
        metrics = tracker.track_completion("simple-question-answering", question)
        if metrics['success']:
            print(f"✅ Answer: {metrics['answer'][:100]}...")
            print(f"⏱️  Duration: {metrics['duration_ms']:.2f}ms")
            print(f"🎫 Tokens: {metrics['input_tokens']} in / {metrics['output_tokens']} out")
        else:
            print(f"❌ Error: {metrics['error']}")

        time.sleep(1)  # Rate limiting

    # Print summary
    print(tracker.get_summary())
```

### Step 2: View Metrics in LaunchDarkly Dashboard

1. Go to **AI Configs** → Select your config
2. Click **Monitoring** tab
3. You'll see graphs for:
   - Generation count over time
   - Input/Output tokens
   - Duration (p50, p95, p99)
   - Error rate

---

## Use Case 4: A/B Testing with Experiments

**Goal:** Run an experiment to compare model performance
**Complexity:** ⭐⭐⭐ Intermediate-Advanced
**Time:** 30 minutes
**Builds on:** Use Case 3

### Experiment Goal:
**Hypothesis:** Claude Haiku (fast model) has lower time-to-first-token than Sonnet, with acceptable quality

### Step 1: Create Metric in LaunchDarkly

1. Go to **Experiments** → **Metrics** → **Create metric**
2. Fill in:
   - **Name:** `time-to-first-token-avg`
   - **Key:** `ttft-avg`
   - **Kind:** Numeric (average)
   - **Unit:** milliseconds
   - **Analysis method:** Average
3. Click **Save**

### Step 2: Create AI Config with Variations

1. Create new AI Config: `experiment-query-handler`
2. Under **Targeting**, click **Add targeting rule**
3. Create two variations:
   - **Variation 1 (control):** Use `claude-sonnet-bedrock` model
   - **Variation 2 (treatment):** Use `claude-haiku-bedrock` model
4. Save both variations with same prompts

### Step 3: Create Experiment

1. Go to **Experiments** → **Create experiment**
2. Fill in:
   - **Name:** `Model Latency Comparison`
   - **Hypothesis:** "Haiku model reduces time to first token by 30%"
   - **AI Config:** `experiment-query-handler`
   - **Primary metric:** `time-to-first-token-avg` (select "decrease" as goal)
   - **Variations:** 50% Sonnet / 50% Haiku
3. Click **Start experiment**

### Step 4: Run Experiment Code

**CRITICAL:** Use unique request IDs for proper randomization!

**Python:**
```python
import os
import time
import uuid
import boto3
import ldclient
from ldclient import Context
from ldclient.config import Config
from ldai.client import LDAIClient, AICompletionConfigDefault
from dotenv import load_dotenv

load_dotenv()

# Initialize clients once
ldclient.set_config(Config(os.getenv('LAUNCHDARKLY_SDK_KEY')))
ld_client = ldclient.get()
aiclient = LDAIClient(ld_client)
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

class ExperimentRunner:
    def __init__(self):
        self.results = {'sonnet': [], 'haiku': []}

    def run_experiment_query(self, question):
        """Execute query and track TTFT"""
        # ⚠️ CRITICAL: Use unique request ID per request for proper experiment randomization
        request_id = str(uuid.uuid4())

        # Create context
        context = Context.builder(request_id).build()

        # Get AI Config from LaunchDarkly
        fallback = AICompletionConfigDefault(enabled=False)
        config = aiclient.config("experiment-query-handler", context, fallback)

        if not config.enabled:
            print("AI Config is disabled")
            return None

        # Track time to first token (approximate with start time)
        start_time = time.time()

        try:
            # Build messages
            system_msgs = [{"text": msg.content} for msg in config.messages if msg.role == "system"]
            messages = [{"role": "user", "content": [{"text": question}]}]

            # Call Bedrock
            response = bedrock.converse(
                modelId=config.model.name,
                system=system_msgs,
                messages=messages
            )

            # Calculate TTFT (time to first token)
            ttft = (time.time() - start_time) * 1000  # Convert to ms

            # Track metric via tracker
            tracker = getattr(config, 'tracker', None)
            if tracker:
                tracker.track_duration(ttft / 1000)

            # Store result
            model_used = config.model.name
            result = {
                'request_id': request_id,
                'question': question,
                'ttft_ms': ttft,
                'model': model_used,
                'success': True
            }

            # Categorize by model
            if 'haiku' in model_used.lower():
                self.results['haiku'].append(result)
            else:
                self.results['sonnet'].append(result)

            return result

        except Exception as e:
            print(f"Error: {e}")
            return None

    def run_experiment(self, num_requests=50):
        """Run experiment with multiple requests"""
        questions = [
            "What is the capital of France?",
            "Explain machine learning",
            "What is 2+2?",
            "How does gravity work?",
            "Who wrote Hamlet?",
            "What causes rain?",
            "Explain photosynthesis",
            "What is DNA?",
            "How do computers work?",
            "What is the speed of light?"
        ]

        print(f"🧪 Running experiment with {num_requests} requests...\n")

        for i in range(num_requests):
            question = questions[i % len(questions)]
            result = self.run_experiment_query(question)

            if result:
                model_emoji = "⚡" if 'haiku' in result['model'].lower() else "🧠"
                print(f"{model_emoji} Request {i+1}: {result['ttft_ms']:.2f}ms - {result['model']}")

            time.sleep(0.5)  # Rate limiting

        self.print_results()

    def print_results(self):
        """Print experiment results summary"""
        sonnet_ttfts = [r['ttft_ms'] for r in self.results['sonnet']]
        haiku_ttfts = [r['ttft_ms'] for r in self.results['haiku']]

        print(f"\n{'='*60}")
        print("📊 EXPERIMENT RESULTS")
        print(f"{'='*60}")
        print(f"Sonnet requests: {len(sonnet_ttfts)}")
        print(f"Haiku requests: {len(haiku_ttfts)}")

        if sonnet_ttfts:
            avg_sonnet = sum(sonnet_ttfts) / len(sonnet_ttfts)
            print(f"\n🧠 Sonnet Avg TTFT: {avg_sonnet:.2f}ms")

        if haiku_ttfts:
            avg_haiku = sum(haiku_ttfts) / len(haiku_ttfts)
            print(f"⚡ Haiku Avg TTFT: {avg_haiku:.2f}ms")

        if sonnet_ttfts and haiku_ttfts:
            improvement = ((avg_sonnet - avg_haiku) / avg_sonnet) * 100
            print(f"\n💡 Haiku is {improvement:.1f}% faster")

        print(f"\n{'='*60}")
        print("📈 View detailed results in LaunchDarkly Experiments dashboard")

    def close(self):
        self.client.close()

# Run the experiment
if __name__ == "__main__":
    runner = ExperimentRunner(os.getenv('LAUNCHDARKLY_SDK_KEY'))
    runner.run_experiment(num_requests=50)
    runner.close()
```

### Step 5: Analyze Results in LaunchDarkly

1. Go to **Experiments** → Select `Model Latency Comparison`
2. View:
   - Traffic distribution (should be ~50/50)
   - Primary metric results (TTFT comparison)
   - Statistical significance
   - Confidence intervals
3. Check "Health check" panel for experiment validation

### Expected Results:
- Haiku should show 30-50% lower TTFT
- LaunchDarkly will calculate statistical significance
- If p-value < 0.05, results are statistically significant

---

## Use Case 5: Dynamic Prompts with Variables

**Goal:** Create reusable AI Configs with dynamic prompt variables
**Complexity:** ⭐⭐ Intermediate
**Time:** 20 minutes
**Builds on:** Use Case 1

### Use Case: Customer Support Response Generator

Create an AI Config that generates customer support responses with customizable:
- Customer name
- Issue type
- Product name
- Tone (formal/casual)

### Step 1: Create AI Config with Variables

1. Create new AI Config: `customer-support-generator`
2. Select model: `claude-sonnet-bedrock`
3. System prompt:
   ```
   You are a {{tone}} customer support representative for {{company_name}}.
   Your goal is to provide helpful, empathetic responses to customer issues.
   ```
4. User prompt:
   ```
   Customer Name: {{customer_name}}
   Product: {{product_name}}
   Issue Type: {{issue_type}}
   Customer Message: {{customer_message}}

   Generate a support response that:
   1. Acknowledges the issue
   2. Provides a solution or next steps
   3. Maintains a {{tone}} tone
   4. Includes a ticket number reference: {{ticket_number}}
   ```

### Step 2: Use Dynamic Variables

**Python:**
```python
import os
import uuid
from launchdarkly_server_sdk import Context, LDClient
from dotenv import load_dotenv

load_dotenv()

class CustomerSupportAI:
    def __init__(self, sdk_key, company_name="TechCorp"):
        self.client = LDClient(sdk_key)
        self.company_name = company_name

    def generate_response(self, customer_name, product_name, issue_type,
                         customer_message, tone="professional"):
        """Generate customer support response"""
        # Create unique context
        context = Context.builder(str(uuid.uuid4())).kind("request").build()

        # Get AI Config
        ai_config = self.client.get_ai_config("customer-support-generator", context)

        # Prepare variables
        variables = {
            "customer_name": customer_name,
            "product_name": product_name,
            "issue_type": issue_type,
            "customer_message": customer_message,
            "tone": tone,
            "company_name": self.company_name,
            "ticket_number": f"TK-{uuid.uuid4().hex[:8].upper()}"
        }

        # Execute
        response = ai_config.execute(variables)
        return response['content']

    def close(self):
        self.client.close()

# Test with different scenarios
if __name__ == "__main__":
    support_ai = CustomerSupportAI(
        os.getenv('LAUNCHDARKLY_SDK_KEY'),
        company_name="CloudServices Inc"
    )

    # Scenario 1: Billing issue (formal tone)
    print("📧 SCENARIO 1: Billing Issue (Formal)")
    print("="*60)
    response = support_ai.generate_response(
        customer_name="John Smith",
        product_name="Premium Cloud Storage",
        issue_type="Billing",
        customer_message="I was charged twice for my monthly subscription.",
        tone="professional and formal"
    )
    print(response)
    print("\n")

    # Scenario 2: Technical issue (casual tone)
    print("📧 SCENARIO 2: Technical Issue (Casual)")
    print("="*60)
    response = support_ai.generate_response(
        customer_name="Sarah",
        product_name="Mobile App",
        issue_type="Technical",
        customer_message="The app keeps crashing when I try to upload files.",
        tone="friendly and casual"
    )
    print(response)
    print("\n")

    # Scenario 3: Feature request (professional tone)
    print("📧 SCENARIO 3: Feature Request")
    print("="*60)
    response = support_ai.generate_response(
        customer_name="Mike Chen",
        product_name="API Service",
        issue_type="Feature Request",
        customer_message="Can you add support for webhooks?",
        tone="professional"
    )
    print(response)

    support_ai.close()
```

### Benefits of Dynamic Prompts:
- ✅ Reusable across multiple scenarios
- ✅ Easy to update prompts without code changes
- ✅ Consistent formatting and structure
- ✅ Version control through LaunchDarkly UI

---

## Use Case 6: Environment-Based Targeting

**Goal:** Different AI Config behavior per environment (dev/staging/prod)
**Complexity:** ⭐⭐⭐ Advanced
**Time:** 25 minutes
**Builds on:** Previous use cases

### Use Case: Different Models per Environment

- **Development:** Use Haiku (fast, cheap) for rapid testing
- **Staging:** Use Sonnet (balanced) for realistic testing
- **Production:** Use Opus (best quality) for customers

### Step 1: Create Environment-Specific Contexts

**Python:**
```python
import os
from launchdarkly_server_sdk import Context, LDClient
from dotenv import load_dotenv

load_dotenv()

class EnvironmentAwareAI:
    def __init__(self, sdk_key, environment="development"):
        self.client = LDClient(sdk_key)
        self.environment = environment

    def query(self, question, user_id="anonymous"):
        """Execute query with environment context"""
        # Create context with environment attribute
        context = (Context.builder(user_id)
                  .kind("user")
                  .set("environment", self.environment)
                  .build())

        # Get AI Config (will vary by environment targeting)
        ai_config = self.client.get_ai_config("environment-aware-assistant", context)

        response = ai_config.execute({"question": question})

        print(f"🌍 Environment: {self.environment}")
        print(f"🤖 Model used: {response.get('model', 'unknown')}")
        print(f"💬 Response: {response['content']}\n")

        return response

    def close(self):
        self.client.close()

# Test across environments
if __name__ == "__main__":
    question = "Explain cloud computing"

    # Development environment
    dev_ai = EnvironmentAwareAI(
        os.getenv('LAUNCHDARKLY_SDK_KEY'),
        environment="development"
    )
    dev_ai.query(question)
    dev_ai.close()

    # Production environment
    prod_ai = EnvironmentAwareAI(
        os.getenv('LAUNCHDARKLY_SDK_KEY'),
        environment="production"
    )
    prod_ai.query(question)
    prod_ai.close()
```

### Step 2: Configure Targeting in LaunchDarkly

1. Go to your AI Config: `environment-aware-assistant`
2. Under **Targeting**, click **Add rule**
3. Create rules:

   **Rule 1: Development**
   - If `environment` is `development`
   - Serve variation: Haiku model

   **Rule 2: Staging**
   - If `environment` is `staging`
   - Serve variation: Sonnet model

   **Rule 3: Production**
   - If `environment` is `production`
   - Serve variation: Opus model

4. Set default variation: Haiku (fallback)

### Advanced: Percentage Rollout in Production

Gradually roll out new model to production:

1. In Production rule, click **Percentage rollout**
2. Set:
   - 90% → Sonnet (current)
   - 10% → Opus (new model)
3. Monitor metrics
4. Gradually increase Opus to 25%, 50%, 75%, 100%

---

## Use Case 7: Online Evaluations (AI Judges)

**Goal:** Automatically evaluate AI response quality in production
**Complexity:** ⭐⭐⭐⭐ Advanced
**Time:** 30 minutes
**Builds on:** All previous use cases

### What Are AI Judges?

AI Judges are special AI Configs that evaluate other AI Config outputs for:
- **Accuracy:** Is the answer correct?
- **Relevance:** Does it answer the question?
- **Toxicity:** Is it safe and appropriate?
- **Hallucination:** Is it making up facts?

### Step 1: Enable Built-in Judges

LaunchDarkly provides three default judges:

1. Go to your AI Config
2. Click **Evaluations** tab
3. Enable judges:
   - ✅ **Relevance Judge**
   - ✅ **Toxicity Judge**
   - ✅ **Answer Relevance Judge**

### Step 2: Create Custom Judge (Optional)

For specialized evaluation criteria:

1. Create new AI Config: `accuracy-judge`
2. Type: **Agent-based** (for judges)
3. System prompt:
   ```
   You are an accuracy evaluator. Score the AI response on how factually correct it is.

   Scoring:
   1 = Completely incorrect or fabricated
   2 = Mostly incorrect with some truth
   3 = Partially correct
   4 = Mostly correct with minor errors
   5 = Completely accurate

   Consider:
   - Are facts verifiable?
   - Are there logical inconsistencies?
   - Is anything made up or hallucinated?
   ```
4. User prompt:
   ```
   Question: {{question}}
   AI Response: {{response}}

   Evaluate the accuracy and respond with:
   {
     "score": <1-5>,
     "reasoning": "<brief explanation>",
     "concerns": ["<any specific issues>"]
   }
   ```

### Step 3: Track Judge Scores

**Python:**
```python
import os
import uuid
import json
from launchdarkly_server_sdk import Context, LDClient
from dotenv import load_dotenv

load_dotenv()

class EvaluatedAI:
    def __init__(self, sdk_key):
        self.client = LDClient(sdk_key)

    def query_with_evaluation(self, question):
        """Execute query and evaluate response"""
        # Generate response
        context = Context.builder(str(uuid.uuid4())).kind("request").build()
        ai_config = self.client.get_ai_config("simple-question-answering", context)
        response = ai_config.execute({"question": question})

        ai_response = response['content']

        # Evaluate with custom judge
        judge_context = Context.builder(str(uuid.uuid4())).kind("request").build()
        judge_config = self.client.get_ai_config("accuracy-judge", judge_context)

        evaluation = judge_config.execute({
            "question": question,
            "response": ai_response
        })

        # Parse judge response
        try:
            eval_result = json.loads(evaluation['content'])
            score = eval_result.get('score', 0)
            reasoning = eval_result.get('reasoning', '')
            concerns = eval_result.get('concerns', [])
        except:
            # Fallback if judge doesn't return JSON
            score = 0
            reasoning = evaluation['content']
            concerns = []

        # Track evaluation metric
        self.client.track("accuracy-score", context, metric_value=score)

        return {
            "question": question,
            "response": ai_response,
            "evaluation": {
                "score": score,
                "reasoning": reasoning,
                "concerns": concerns
            }
        }

    def close(self):
        self.client.close()

# Test with evaluation
if __name__ == "__main__":
    eval_ai = EvaluatedAI(os.getenv('LAUNCHDARKLY_SDK_KEY'))

    test_questions = [
        "What is the capital of France?",
        "How many planets are in our solar system?",
        "Who was the first president of the United States?",
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")

        result = eval_ai.query_with_evaluation(question)

        print(f"💬 Response: {result['response']}")
        print(f"\n📊 Evaluation:")
        print(f"   Score: {result['evaluation']['score']}/5")
        print(f"   Reasoning: {result['evaluation']['reasoning']}")
        if result['evaluation']['concerns']:
            print(f"   ⚠️  Concerns: {', '.join(result['evaluation']['concerns'])}")

    eval_ai.close()
```

### Step 4: View Evaluation Metrics

1. Go to AI Config → **Monitoring** tab
2. You'll see evaluation scores alongside performance metrics
3. Can set up alerts for low scores

### Important Note:

⚠️ **JS SDK Only:** Online evaluations are currently only supported in JavaScript SDK. For Python, you need to:
- Wait for Python SDK support (estimated by Dec 2025 in original docs)
- Or implement custom evaluation tracking as shown above

---

## Troubleshooting Guide

### Issue 1: Experiment Not Randomizing (All requests get same variation)

**Symptoms:**
- 100% traffic going to one variation
- Expected 50/50 split not happening

**Solution:**
```python
# ❌ WRONG - Same context key every time
context = Context.builder("anonymous").kind("request").build()

# ✅ CORRECT - Unique key per request
import uuid
context = Context.builder(str(uuid.uuid4())).kind("request").build()
```

**Why:** LaunchDarkly hashes the context key to determine variation. Same key = same hash = same variation.

### Issue 2: SDK Key vs API Key Confusion

**Symptoms:**
- Authentication errors
- "Invalid key" errors

**Solution:**
- Use **SDK key** for application code (starts with `sdk-`)
- Use **API key** only for management API operations
- Get SDK key from: **Account Settings → Environments → SDK key**

### Issue 3: Metrics Not Appearing in Dashboard

**Symptoms:**
- Monitoring tab shows no data
- Graphs are empty

**Solutions:**
1. Wait 5-10 minutes (LaunchDarkly has ~5min delay)
2. Ensure you're using `track()` method correctly
3. Check you're viewing correct environment
4. Verify SDK is properly initialized

### Issue 4: AWS Bedrock Access Denied

**Symptoms:**
- Error: "Access denied to model"
- "Model not available in region"

**Solutions:**
1. Request model access in AWS Console:
   - Go to AWS Bedrock console
   - Navigate to "Model access"
   - Request access to Claude models
   - Wait for approval (can take 24-48 hours)

2. Verify region:
   ```python
   # Claude models available in limited regions
   # Try: us-east-1, us-west-2, eu-west-1
   bedrock = boto3.client(
       service_name='bedrock-runtime',
       region_name='us-east-1'  # Try different regions
   )
   ```

### Issue 5: "Cannot edit Model Config after creation"

**Symptoms:**
- Want to change model parameters
- Can't edit custom parameters

**Workaround:**
1. Create new Model Config with desired settings
2. Update AI Configs to reference new Model Config
3. Delete old Model Config

**Note:** This is a LaunchDarkly limitation mentioned in Veeam docs.

### Issue 6: Percentile Metrics (p95) Not Showing Results

**Symptoms:**
- Experiment results tab showing error
- "Percentile analysis methods in beta"

**Solution:**
- Use **average** metrics instead of percentile for experiments
- Percentile analysis doesn't support CUPED adjustments yet
- Recreate experiment with average as primary metric

---

## Next Steps & Advanced Topics

### Combine Multiple Use Cases:

**Production-Ready AI Service:**
```python
class ProductionAIService:
    def __init__(self, sdk_key, environment):
        self.client = LDClient(sdk_key)
        self.environment = environment
        self.metrics_tracker = MetricsTracker(sdk_key)

    def smart_query(self, question, user_id):
        """
        - Routes to appropriate model (fast vs strong)
        - Tracks comprehensive metrics
        - Evaluates response quality
        - Handles errors gracefully
        - Environment-aware targeting
        """
        pass  # Combine all use cases here
```

### Additional Topics to Explore:

1. **Multi-step Agent Workflows**
   - Tool calling
   - Sequential reasoning
   - State management

2. **Cost Optimization**
   - Cache frequently asked questions
   - Smart model routing
   - Token budget management

3. **Quality Assurance**
   - A/B test prompt variations
   - Compare model outputs
   - Regression testing

4. **Guardrails**
   - Content filtering
   - PII detection
   - Rate limiting

5. **Observability**
   - Distributed tracing
   - Log aggregation
   - Real-time monitoring

---

## Summary: Key Learnings

### 1. AWS Bedrock Simplicity
✅ Standardized endpoints per region (easier than Azure)
✅ No custom parameters needed
✅ Simple model selection

### 2. Critical Implementation Details
⚠️ **MUST use unique request IDs** for experiments to work
⚠️ Use SDK key (not API key) in application code
⚠️ LaunchDarkly metrics have ~5min delay

### 3. Best Practices
1. Start simple (Use Case 1) before adding complexity
2. Always track metrics from day one
3. Use experiments to validate assumptions
4. Dynamic prompts = more maintainable
5. Environment-based targeting for safe rollouts

### 4. Current Limitations (as of doc date)
- Online evaluations: JS SDK only (Python coming soon)
- Model configs: Can't edit after creation
- Percentile metrics: No CUPED support yet

---

## Resources

- **LaunchDarkly AI Configs Docs:** https://docs.launchdarkly.com/home/ai
- **AWS Bedrock Models:** https://aws.amazon.com/bedrock/
- **LaunchDarkly SDKs:** https://docs.launchdarkly.com/sdk/
- **Original Veeam Evaluation:** See `Veeam_LaunchDarkly_AI_Configs_Analysis.md`

---

**Last Updated:** 2026-02-02
**Tutorial Version:** 1.0
**Tested with:** LaunchDarkly Python SDK, AWS Bedrock (us-east-1)
