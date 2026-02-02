# Detailed Call Flow: /api/chat

This diagram traces a single chat request from user click to AI response, with exact line numbers.

```mermaid
flowchart TB
    subgraph indexHTML ["static/index.html"]
        A["L422: sendMessage()"]
        B["L444: fetch /api/chat"]
        C["L464: addMessage response"]
    end

    subgraph appPY ["app.py"]
        D["L46: @app.route /api/chat"]
        E["L60: get_or_create_chat_session()"]
        F["L71: chat.chat(message)"]
        G["L75: return jsonify response"]
    end

    subgraph chatPY ["chat_interaction.py"]
        H["L62: initialize()"]
        I["L66: aiclient.config()"]
        J["L270: chat()"]
        K["L272: invoke_bedrock()"]
        L["L153: get_bedrock_client()"]
        M["L154: bedrock_client.converse()"]
        N["L183: return response"]
    end

    subgraph external ["External"]
        LD["LaunchDarkly"]
        AWS["AWS Bedrock"]
    end

    A --> B
    B --> D
    D --> E
    E --> H
    H --> I
    I --> LD
    LD -->|"model, messages"| I
    E --> F
    F --> J
    J --> K
    K --> L
    L --> M
    M --> AWS
    AWS -->|"AI response"| M
    M --> N
    N --> G
    G --> B
    B --> C
```

## Step-by-Step with Line Numbers

| Step | File | Line | What Happens |
|------|------|------|--------------|
| 1 | `index.html` | 422 | User clicks Send → `sendMessage()` called |
| 2 | `index.html` | 444 | `fetch('/api/chat', {...})` sends POST request |
| 3 | `app.py` | 46 | Flask route `/api/chat` receives request |
| 4 | `app.py` | 60 | `get_or_create_chat_session()` called |
| 5 | `chat_interaction.py` | 62 | `ChatInteraction.initialize()` called |
| 6 | `chat_interaction.py` | 66 | `aiclient.config()` fetches AI Config from LaunchDarkly |
| 7 | `app.py` | 71 | `chat.chat(message)` called |
| 8 | `chat_interaction.py` | 270 | `chat()` method called |
| 9 | `chat_interaction.py` | 272 | `invoke_bedrock()` called |
| 10 | `chat_interaction.py` | 153 | `get_bedrock_client()` creates AWS client |
| 11 | `chat_interaction.py` | 154 | `bedrock_client.converse()` calls AWS Bedrock |
| 12 | `chat_interaction.py` | 183 | Response returned from `invoke_bedrock()` |
| 13 | `app.py` | 75 | `jsonify()` sends JSON response to frontend |
| 14 | `index.html` | 464 | `addMessage()` displays AI response in chat |
