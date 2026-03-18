import subprocess
from typing import List


class CommandLLM:
    def __init__(self, cmd: List[str]):
        if not cmd:
            raise ValueError("llm cmd is empty")
        self.cmd = cmd

    def generate(self, prompt: str) -> str:
        completed = subprocess.run(
            self.cmd,
            input=prompt,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"LLM command failed (code {completed.returncode}): {completed.stderr.strip()}"
            )
        return completed.stdout.strip()
