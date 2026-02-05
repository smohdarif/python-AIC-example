# LaunchDarkly AI Configs + AWS Bedrock Chat Example

This example demonstrates how to create a web-based chat interface using LaunchDarkly AI Configs and AWS Bedrock with Amazon Nova Pro.

## Features

- **Web Interface**: Beautiful, modern chat UI for interactive conversations
- **Dynamic AI Configuration**: Uses LaunchDarkly AI Configs to manage AI model settings, prompts, and behavior
- **AWS Bedrock Integration**: Leverages AWS Bedrock for AI model inference
- **LLM Judge Pattern**: Optional evaluation of chat responses using a separate AI Config judge
- **Conversation Management**: Maintains conversation history across multiple turns
- **Metrics Tracking**: Tracks duration and token usage for AI interactions
- **Session Management**: Supports multiple chat sessions

## Prerequisites

1. **LaunchDarkly Account**: 
   - Create an AI Config in your LaunchDarkly project (`nteixeira-ld-demo`)
   - Get your SDK key from LaunchDarkly settings

2. **AWS Account**:
   - Configure AWS credentials with Bedrock access
   - Ensure you have access to Amazon Nova Pro model (or your preferred Bedrock model)

3. **Python 3.8+**

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:

Create a `.env` file in the project root:
```bash
# LaunchDarkly Configuration
LAUNCHDARKLY_SDK_KEY=your-launchdarkly-sdk-key-here
LAUNCHDARKLY_AI_CONFIG_KEY=chat-assistant-config
LAUNCHDARKLY_JUDGE_CONFIG_KEY=ld-ai-judge-accuracy  # Optional: AI Config key for LLM judge evaluation

# AWS Configuration
# Note: AWS credentials can be provided via:
# - AWS SSO profile (recommended): Set AWS_PROFILE and run 'aws sso login --profile <profile>'
# - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
# - AWS credentials file (~/.aws/credentials)
# - IAM roles (if running on EC2/ECS/Lambda)
AWS_REGION=us-east-1
AWS_PROFILE=aiconfigdemo  # Optional: specify AWS profile name (defaults to 'aiconfigdemo')

# Optional: Server Configuration
PORT=5000
```

3. **Create AI Configs in LaunchDarkly**:
   - Go to your LaunchDarkly project (`nteixeira-ld-demo`)
   
   - **Chat AI Config**: Create a new AI Config with key `chat-assistant-config` (or update the key in `.env`)
     - Configure the model (e.g., `amazon.nova-pro-v1:0` for Amazon Nova Pro)
     - Set up system messages/prompts as needed
     - For a simple setup, keep a single variation and set targeting to serve all contexts
   
   - **Judge AI Config** (Optional): Create a judge AI Config with key `ld-ai-judge-accuracy` (or update the key in `.env`)
     - Configure a judge model (typically a different model than the chat model)
     - Set up system messages/prompts that instruct the judge on how to evaluate responses
     - The judge will evaluate chat input/output pairs and provide evaluation feedback

## Usage

### Start the Web Server

```bash
python app.py
```

The server will start on `http://localhost:5000` (or the port specified in your `.env` file).

### Access the Chat Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

You can now:
- Type messages in the input field
- Press Enter or click "Send" to send messages
- Click "Reset" to clear the conversation history
- View the conversation history in real-time

## API Endpoints

The Flask backend provides the following REST API endpoints:

### POST `/api/chat`
Send a chat message and receive an AI response.

**Request:**
```json
{
  "message": "Hello!",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id",
  "email": "optional-email"
}
```

**Response (without judge):**
```json
{
  "response": "Hello! How can I help you?",
  "session_id": "session-id",
  "model": "anthropic.claude-3-sonnet-20240229-v1:0"
}
```

**Response (with judge, when a judge AI Config is enabled):**
```json
{
  "response": "Hello! How can I help you?",
  "judge": {
    "evaluation": "The response is appropriate and helpful...",
    "usage": {"inputTokens": 50, "outputTokens": 30}
  },
  "session_id": "session-id",
  "model": "amazon.nova-pro-v1:0"
}
```

### GET `/api/history?session_id=<session_id>`
Get conversation history for a session.

**Response:**
```json
{
  "history": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hello! How can I help you?"}
  ]
}
```

### POST `/api/reset`
Reset conversation history for a session.

**Request:**
```json
{
  "session_id": "session-id"
}
```

### GET `/api/health`
Health check endpoint.

## Targeting Notes

The LaunchDarkly context includes:

- `key` (from `user_id`, or `user-<session_id>` if not provided)
- `email` (from request, or a default email if not provided)

For initial testing, use a single variation and serve all contexts. If you
later want multiple variations, target by `key` or `email`.

## Project Structure

```
python-AIC-example/
├── app.py                 # Flask web server
├── chat_interaction.py    # Core chat interaction logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   └── index.html        # Frontend chat interface
└── .env                  # Environment variables (create this)
```

## Customization

### Change Port

Set the `PORT` environment variable or modify `app.py`:

```python
port = int(os.getenv('PORT', 5000))
```

### Different Bedrock Models

The model is configured in your LaunchDarkly AI Config. This example uses Amazon Nova Pro, but other Bedrock models are supported:
- `amazon.nova-pro-v1:0` - Amazon Nova Pro (recommended)
- `amazon.nova-lite-v1:0` - Amazon Nova Lite
- `anthropic.claude-3-sonnet-20240229-v1:0` - Claude 3 Sonnet
- `anthropic.claude-3-haiku-20240307-v1:0` - Claude 3 Haiku
- `anthropic.claude-3-opus-20240229-v1:0` - Claude 3 Opus
- Other Bedrock models as available

### Styling

Modify `static/index.html` to customize the chat interface appearance.

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (Frontend UI)  │
└────────┬────────┘
         │
         │ HTTP Requests
         ▼
┌─────────────────┐
│   Flask Server  │
│   (app.py)      │
└────────┬────────┘
         │
         │ Uses
         ▼
┌─────────────────┐
│ ChatInteraction │
│   (chat_interaction.py) │
└────────┬────────┘
         │
         ├─► LaunchDarkly AI Configs
         │
         └─► AWS Bedrock (Amazon Nova Pro)
```

## Notes

- The example uses AWS Bedrock Converse API which works with Amazon Nova Pro and other Bedrock models
- The message format is handled automatically by the Bedrock Converse API
- Metrics are tracked automatically via the LaunchDarkly tracker
- Conversation history is maintained in memory per session (in production, use a proper session store like Redis)
- The LaunchDarkly client is initialized once and shared across requests

## Troubleshooting

- **"AI Config is disabled"**: Check your LaunchDarkly AI Config targeting rules
- **AWS errors**: Verify your AWS credentials and Bedrock model access
- **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
- **CORS errors**: The Flask app includes CORS support, but if you encounter issues, check the `flask-cors` configuration
- **Port already in use**: Change the `PORT` environment variable or kill the process using the port

## Development

For development with auto-reload:

```bash
export FLASK_ENV=development
python app.py
```

Or use Flask's built-in development server with debug mode (already enabled in `app.py`).

---

## 📖 Documentation & Coding Guidelines

### For Contributors and AI Assistants

**⚠️ MANDATORY:** All code must follow the official Python AI SDK patterns in this repository.

- **Coding Guidelines:** [`CODING_GUIDELINES.md`](CODING_GUIDELINES.md)
- **Documentation Index:** [`docs/README.md`](docs/README.md)
- **Verified Code Examples:** [`docs/SDK_Code_Examples_CORRECTED.md`](docs/SDK_Code_Examples_CORRECTED.md)

**Key Rule:** Always reference `/python-server-sdk-ai/` for API patterns. Never use generic LaunchDarkly documentation patterns.

### Official SDK Reference

All code in this repository is based on:
```
/python-server-sdk-ai/packages/sdk/server-ai/
```

See `CODING_GUIDELINES.md` for mandatory patterns and verification process.

---

## 📚 Additional Resources

### Implementation Guides

This repository includes comprehensive guides for implementing LaunchDarkly AI Configs:

- **Business Case & ROI:** `docs/LaunchDarkly_Implementation_Executive_Summary.md`
- **8-10 Week Plan:** `docs/LaunchDarkly_AI_Configs_Implementation_Plan.md`
- **Code Examples:** `docs/SDK_Code_Examples_CORRECTED.md`
- **Tutorials:** `docs/LaunchDarkly_AI_Configs_Tutorial.md`
- **Production Learnings:** `docs/Veeam_LaunchDarkly_AI_Configs_Analysis.md`

See `docs/README.md` for complete documentation navigation.

---

