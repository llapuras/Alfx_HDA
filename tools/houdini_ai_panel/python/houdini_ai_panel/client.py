"""OpenAI client with no third-party dependency requirement."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5-mini"


SYSTEM_PROMPT = """You are an expert Houdini TD assistant embedded inside Houdini.
You can inspect context supplied by the panel, but you cannot directly mutate the scene.
When the user wants scene changes, explain the approach and include one Python code block
using HOM. The user must review and confirm code before it is executed.
Keep answers concise, practical, and Houdini-specific.
"""


def _extract_text(payload):
    chunks = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in ("output_text", "text"):
                text = content.get("text")
                if text:
                    chunks.append(text)
    if chunks:
        return "\n".join(chunks)
    if payload.get("output_text"):
        return payload["output_text"]
    return json.dumps(payload, ensure_ascii=False, indent=2)


class OpenAIChatClient(object):
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL

    def complete(self, user_message, context, history=None):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment Houdini was launched from.")

        history = history or []
        input_messages = []
        input_messages.extend(history[-12:])
        input_messages.append(
            {
                "role": "user",
                "content": "Houdini context JSON:\n%s\n\nUser question:\n%s"
                % (json.dumps(context, ensure_ascii=False, indent=2), user_message),
            }
        )

        body = {
            "model": self.model,
            "instructions": SYSTEM_PROMPT,
            "input": input_messages,
        }
        request = urllib.request.Request(
            OPENAI_RESPONSES_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": "Bearer %s" % self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise RuntimeError("OpenAI API error %s: %s" % (exc.code, detail))
        except urllib.error.URLError as exc:
            raise RuntimeError("Could not reach OpenAI API: %s" % exc)

        return _extract_text(payload)
