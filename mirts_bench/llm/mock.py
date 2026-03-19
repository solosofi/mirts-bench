import json


class MockLLM:
    def generate(self, prompt: str) -> str:
        _ = prompt
        return json.dumps({"type": "end_turn"})
