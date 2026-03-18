import json
import urllib.error
import urllib.request
from typing import Optional


def _normalize_url(host: str) -> str:
    value = host.strip()
    if not value.startswith("http://") and not value.startswith("https://"):
        value = "https://" + value
    value = value.rstrip("/")

    if value.endswith("/v1/chat/completions") or value.endswith("/chat/completions"):
        return value
    if value.endswith("/v1"):
        return value + "/chat/completions"
    return value + "/v1/chat/completions"


class HttpLLM:
    def __init__(self, host: str, model: str, api_key: Optional[str] = None, timeout: int = 60):
        if not host:
            raise ValueError("llm host is required")
        if not model:
            raise ValueError("llm model is required")
        self.url = _normalize_url(host)
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }
        data = json.dumps(payload).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"LLM HTTP error {exc.code}: {detail[:1000]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM HTTP error: {exc}") from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"LLM response was not valid JSON: {body[:1000]}"
            ) from exc

        content = None
        try:
            choice = data["choices"][0]
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict) and "content" in message:
                content = message["content"]
            elif isinstance(choice, dict) and "text" in choice:
                content = choice["text"]
        except Exception:
            content = None

        if not content:
            raise RuntimeError(
                f"LLM response missing choices[0].message.content: {body[:1000]}"
            )

        return content.strip()
