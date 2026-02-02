# File Flow Diagram

This diagram shows how files in the project call each other.

```mermaid
flowchart TB
    subgraph browser [Browser]
        indexHTML["static/index.html"]
    end

    subgraph server [Flask Server]
        appPY["app.py"]
        chatPY["chat_interaction.py"]
    end

    subgraph external [External Services]
        LD["LaunchDarkly AI Configs"]
        Bedrock["AWS Bedrock"]
    end

    indexHTML -->|"HTTP POST /api/chat"| appPY
    indexHTML -->|"HTTP GET /api/model"| appPY
    indexHTML -->|"HTTP GET /api/history"| appPY
    indexHTML -->|"HTTP POST /api/reset"| appPY

    appPY -->|"imports & calls"| chatPY
    chatPY -->|"aiclient.config()"| LD
    chatPY -->|"bedrock_client.converse()"| Bedrock

    LD -->|"returns model, messages, tracker"| chatPY
    Bedrock -->|"returns AI response"| chatPY
    chatPY -->|"returns response"| appPY
    appPY -->|"JSON response"| indexHTML
```

## File Responsibilities

| File | Role |
|------|------|
| `static/index.html` | Frontend UI, sends HTTP requests, displays chat |
| `app.py` | Flask server, routes, session management |
| `chat_interaction.py` | LaunchDarkly SDK init, Bedrock calls, conversation history |
| `.env` | Environment variables (SDK keys, AWS config) |

## Call Sequence (simplified)

1. **User types message** → `index.html`
2. **POST /api/chat** → `app.py`
3. **get_or_create_chat_session()** → `app.py` calls `ChatInteraction` from `chat_interaction.py`
4. **aiclient.config()** → `chat_interaction.py` fetches AI Config from LaunchDarkly
5. **invoke_bedrock()** → `chat_interaction.py` calls AWS Bedrock with messages
6. **Response flows back** → `chat_interaction.py` → `app.py` → `index.html`
