import json
from pathlib import Path
from typing import Any, Dict, Optional

from .base import GameAdapter


class UIAutomationAdapter(GameAdapter):
    def __init__(self, calibration_path: str = "calibration.json") -> None:
        self.calibration_path = Path(calibration_path)
        self.calibration: Optional[Dict[str, Any]] = None

    def _load_calibration(self) -> None:
        if not self.calibration_path.exists():
            raise NotImplementedError(
                "UI adapter requires a calibration.json file with UI coordinates. "
                "Create it and wire click/ocr logic in ui_automation.py."
            )
        self.calibration = json.loads(self.calibration_path.read_text(encoding="utf-8"))

    def reset(self, difficulty: str, opponents: int, game_index: int) -> None:
        _ = difficulty
        _ = opponents
        _ = game_index
        self._load_calibration()

    def is_done(self) -> bool:
        raise NotImplementedError("UI adapter: implement end-of-game detection")

    def get_state(self) -> Dict[str, Any]:
        raise NotImplementedError(
            "UI adapter: implement state extraction (OCR, memory read, or API)."
        )

    def apply_action(self, action: Dict[str, Any], run_dir: str, turn_index: int) -> None:
        _ = run_dir
        _ = turn_index
        raise NotImplementedError(
            "UI adapter: map action schema to UI clicks/keys using calibration.json."
        )

    def get_result(self) -> Dict[str, Any]:
        raise NotImplementedError("UI adapter: implement result extraction")
