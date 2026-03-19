import json
import urllib.error
import urllib.request
from typing import Optional


def _normalize_url(host: str) -> str:
    value = host.strip()
    if not value.startswith("http://") and not value.startswith("https://"):
        value = "https://" + value
    value = value.rstrip("/")
    if value.endswith("/prompt"):
        return value
    return value + "/prompt"


class KaggleBridgeLLM:
    """
    Calls a Kaggle-hosted bridge endpoint that wraps kaggle_benchmarks LLMs.
    Expected request: { "prompt": "...", "model": "vendor/model" (optional) }
    Expected response: { "content": "..." } or { "text": "..." }.
    """

    def __init__(self, host: str, model: Optional[str] = None, timeout: int = 60):
        if not host:
            raise ValueError("llm host is required")
        self.url = _normalize_url(host)
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        payload = {"prompt": prompt}
        if self.model:
            payload["model"] = self.model
        data = json.dumps(payload).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        request = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"Kaggle bridge HTTP error {exc.code}: {detail[:1000]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Kaggle bridge HTTP error: {exc}") from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Kaggle bridge response was not valid JSON: {body[:1000]}"
            ) from exc

        content = data.get("content") or data.get("text")
        if not content:
            raise RuntimeError(
                f"Kaggle bridge response missing content: {body[:1000]}"
            )
        return str(content).strip()
