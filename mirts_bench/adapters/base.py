from abc import ABC, abstractmethod
from typing import Any, Dict


class GameAdapter(ABC):
    @abstractmethod
    def reset(self, difficulty: str, opponents: int, game_index: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_done(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def apply_action(self, action: Dict[str, Any], run_dir: str, turn_index: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_result(self) -> Dict[str, Any]:
        raise NotImplementedError
