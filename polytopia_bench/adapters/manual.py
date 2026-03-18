import json
from pathlib import Path
from typing import Any, Dict, Optional, List

from .base import GameAdapter


class ManualAdapter(GameAdapter):
    def __init__(self, states_dir: str) -> None:
        self.base_dir = Path(states_dir)
        if not self.base_dir.exists():
            raise ValueError(f"states dir not found: {states_dir}")
        self.game_dir: Optional[Path] = None
        self.state_files: List[Path] = []
        self.index = 0

    def _select_game_dir(self, game_index: int) -> Path:
        candidate = self.base_dir / f"game_{game_index:03d}"
        return candidate if candidate.exists() else self.base_dir

    def reset(self, difficulty: str, opponents: int, game_index: int) -> None:
        _ = difficulty
        _ = opponents
        self.game_dir = self._select_game_dir(game_index)
        self.state_files = sorted(
            p for p in self.game_dir.glob("*.json") if p.name.lower() != "result.json"
        )
        if not self.state_files:
            raise ValueError(f"No state JSON files found in {self.game_dir}")
        self.index = 0

    def is_done(self) -> bool:
        return self.index >= len(self.state_files)

    def get_state(self) -> Dict[str, Any]:
        if self.is_done():
            raise RuntimeError("No more states available")
        path = self.state_files[self.index]
        return json.loads(path.read_text(encoding="utf-8"))

    def apply_action(self, action: Dict[str, Any], run_dir: str, turn_index: int) -> None:
        # Ensure action is present in run output (benchmark also writes it).
        action_path = Path(run_dir) / f"turn_{turn_index:03d}_action.json"
        if not action_path.exists():
            action_path.write_text(json.dumps(action, indent=2), encoding="utf-8")

        print(f"Turn {turn_index:03d} action: {json.dumps(action)}")
        input("Apply this action in-game, then press Enter to continue...")
        self.index += 1

    def _prompt_result(self) -> Dict[str, Any]:
        while True:
            result = input("Result (win/draw/loss): ").strip().lower()
            if result in {"win", "draw", "loss"}:
                break
            print("Invalid result. Use win/draw/loss.")
        score_text = input("Score (optional, press Enter to skip): ").strip()
        score = None
        if score_text:
            try:
                score = float(score_text)
            except ValueError:
                score = None
        data: Dict[str, Any] = {"result": result}
        if score is not None:
            data["score"] = score
        return data

    def get_result(self) -> Dict[str, Any]:
        if self.game_dir is None:
            raise RuntimeError("Adapter not reset")
        result_path = self.game_dir / "result.json"
        if result_path.exists():
            data = json.loads(result_path.read_text(encoding="utf-8"))
            result = data.get("result")
            if result not in {"win", "draw", "loss"}:
                raise ValueError("result.json must include result=win/draw/loss")
            return data
        return self._prompt_result()
