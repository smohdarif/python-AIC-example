# App Flow Diagram

This diagram shows the end-to-end request flow from the web UI to LaunchDarkly
AI Configs and AWS Bedrock, including targeting and prompt assembly.

```mermaid
flowchart TD
    Browser["Browser UI (static/index.html)"] -->|User message + session_id| Flask["Flask API (app.py)"]
    Browser -->|Optional user_id/email| Flask

    Flask -->|Get or create ChatInteraction| Chat["ChatInteraction (chat_interaction.py)"]
    Chat -->|LD context: key, email| LD["LaunchDarkly AI Configs"]
    LD -->|Targeting selects variation| Config["AI Config variation"]

    Config -->|Model + system messages| Chat
    Chat -->|Build messages: system + conversation + user input| Bedrock["AWS Bedrock Converse API"]
    Bedrock -->|Assistant response + usage| Chat
    Chat -->|Response text| Flask
    Flask -->|JSON response| Browser

    Chat -->|Optional judge config| JudgeConfig["Judge AI Config"]
    JudgeConfig -->|Judge prompt| BedrockJudge["AWS Bedrock (judge model)"]
    BedrockJudge -->|Evaluation text + score| Chat
```

## Key Data Elements

- **session_id**: Used to identify chat sessions in memory.
- **user_id / email**: Optional context fields sent to LaunchDarkly for targeting.
- **system messages**: Loaded from the AI Config variation and prepended to the
  conversation for the Bedrock call.
- **user message**: The input text from the UI.
- **assistant response**: The model output returned to the UI.
- **judge evaluation (optional)**: A second model call that scores the response.
