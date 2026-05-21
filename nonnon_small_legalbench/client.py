from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class NonnonClient:
    api_key: str
    base_url: str = "https://small.nonnon.ai/v1"
    timeout_seconds: float = 180.0

    def chat_completion(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 256,
        retries: int = 3,
    ) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout_seconds,
                )
                if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as exc:  # pragma: no cover - network dependent
                last_error = exc
                if attempt < retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                raise
        raise RuntimeError("unreachable") from last_error


def extract_text(response: dict[str, Any]) -> str:
    return str(response["choices"][0]["message"]["content"])
