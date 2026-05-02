import requests
import threading
import time
from pydantic import BaseModel, Field
from website.config import ai_config

_llm_lock = threading.Lock()
_user_priority = threading.Event()


class SimpleScore(BaseModel):
    score: float = Field(..., ge=1, le=10)


def _make_request(messages: list, json_mode: bool) -> str:
    cfg = ai_config()
    headers = {"Authorization": f"Bearer {cfg['api_key']}"}
    headers.update(cfg.get("headers", {}) or {})
    payload = {"model": cfg["model"], "messages": messages}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    response = requests.post(
        url=cfg["api_url"],
        headers=headers,
        json=payload,
        timeout=cfg.get("timeout", 30),
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _post(messages: list, json_mode: bool = True) -> str:
    """Background scoring request — pauses between articles if a user request is waiting."""
    if not ai_config().get("queue_scoring", False):
        return _make_request(messages, json_mode)
    while _user_priority.is_set():
        time.sleep(0.1)
    with _llm_lock:
        return _make_request(messages, json_mode)


def _post_user(messages: list, json_mode: bool = True) -> str:
    """User-facing request — signals scoring to pause, then jumps ahead."""
    if not ai_config().get("queue_scoring", False):
        return _make_request(messages, json_mode)
    _user_priority.set()
    try:
        with _llm_lock:
            return _make_request(messages, json_mode)
    finally:
        _user_priority.clear()


def getCustomScore(text: str, prompt: str) -> float:
    """Score an article 1-10 using a plain-text prompt."""
    content = _post([
        {
            "role": "system",
            "content": (
                f"You are a news article scorer. Score the article 1-10 based on these criteria:\n\n{prompt}\n\n"
                'Return JSON: {"score": <float 1.0-10.0>}'
            ),
        },
        {"role": "user", "content": f"Score this article:\n\n{text}"},
    ])
    result = SimpleScore.model_validate_json(content)
    return round(result.score, 2)


def improve_scoring_prompt(prompt: str) -> str:
    """Rewrite a user's scoring prompt to be clearer and more effective."""
    content = _post_user(
        [
            {
                "role": "system",
                "content": (
                    "You help users write effective prompts for AI-based news article scoring systems. "
                    "The prompt instructs an AI to score articles 1-10."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Rewrite this scoring prompt to be clearer, more specific, and more actionable. "
                    "Keep the same intent. Return only the improved prompt text, nothing else.\n\n"
                    f"Original prompt:\n{prompt}"
                ),
            },
        ],
        json_mode=False,
    )
    return content.strip()
