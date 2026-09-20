# Houdini AI Assistant Panel

This is a local Houdini Python Panel that lets you chat with an OpenAI model from inside Houdini.

## Install

Run this from the repository root:

```powershell
python tools\houdini_ai_panel\scripts\install_package.py
```

Restart Houdini, then open a Python Panel and choose `AI Assistant` from the panel menu.

## Requirements

- Launch Houdini with `OPENAI_API_KEY` set in the environment.
- Optional: set `OPENAI_MODEL`; otherwise the panel uses `gpt-5-mini`.

## Safety

The panel reads scene context automatically, but it does not mutate the scene during chat.
Generated HOM/Python code is copied into the execution preview. It only runs when you press
`Execute Previewed Code`, and the panel saves a timestamped hip backup before running it.

