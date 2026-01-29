# LaunchDarkly AI Configs Notes for This App

This document summarizes the key setup and behavior details we discussed for
the `python-AIC-example` app.

## What the App Uses from LaunchDarkly

- The chat model and prompt are controlled by an AI Config in LaunchDarkly.
- The app reads the config key from `.env`:
  - `LAUNCHDARKLY_AI_CONFIG_KEY` (default: `chat-assistant-config`)
- The app optionally uses a separate AI Config as a judge:
  - `LAUNCHDARKLY_JUDGE_CONFIG_KEY` (default: `ld-ai-judge-accuracy`)

## AI Config Setup Checklist (Chat)

1. Create an AI Config for chat.
2. Set the key to match your `.env` value.
3. Choose a Bedrock model (example: `amazon.nova-pro-v1:0`).
4. Add a **system** message with the main instructions.
5. Publish the config and set targeting to serve **all contexts** while testing.

## Single-Variation Guidance

For simplicity, use **one variation** (for example, `Default`). Targeting can
be set to "serve all contexts" so every user gets the same behavior.

If you later want multiple variations, you can target by `user_id` (context
key) or `email`, which are the only custom fields the app sends.

## System vs User vs Assistant Roles

- **system**: main instructions for behavior (most important).
- **user/assistant**: optional example turns (few-shot) to teach style.

In this app:
- The chat config loads **all** messages into the conversation history, so
  user/assistant examples apply.
- The judge path only uses **system** + **user** messages from the judge config.

## Targeting Inputs from the App

The app sends these context attributes to LaunchDarkly:

- `key`: from `user_id` (or `user-<session_id>` if empty)
- `email`: from the request or a default like `user-<session_id>@example.com`

If you only want a single variation, you can ignore these fields for now.

## Judge Behavior in This App

- The judge is a **second AI call** that evaluates the chat response.
- The judge model is defined by your **judge AI Config** in LaunchDarkly.
- The judge input is built as:

```
Input: <user message>

Output: <assistant response>
```

## How the Judge Score is Extracted

The app tries to parse the judge response as:

- JSON with fields like `score`, `accuracy`, or `accuracy_score`, OR
- plain text that includes `Score: 0.85`

If a score is found, it is sent to LaunchDarkly as the `ai-accuracy` event.

## LD Built-In Judges vs Custom Judge AI Config

- **Built-in judges** (accuracy/relevance/toxicity) are LD-managed evaluators
  attached in the UI.
- **Custom judge AI Config** is what this app uses via
  `LAUNCHDARKLY_JUDGE_CONFIG_KEY`.

If you want to rely on LD built-in judges only, the code would need to be
changed to read those results instead of the custom judge response.
