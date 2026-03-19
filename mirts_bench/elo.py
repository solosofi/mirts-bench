from typing import Literal

Result = Literal["win", "draw", "loss"]


def expected_score(rating: float, opponent_rating: float) -> float:
    return 1.0 / (1.0 + 10 ** ((opponent_rating - rating) / 400.0))


def result_to_score(result: Result) -> float:
    if result == "win":
        return 1.0
    if result == "draw":
        return 0.5
    if result == "loss":
        return 0.0
    raise ValueError(f"Unknown result: {result}")


def update_elo(rating: float, opponent_rating: float, result: Result, k_factor: float = 32.0) -> float:
    expected = expected_score(rating, opponent_rating)
    actual = result_to_score(result)
    return rating + k_factor * (actual - expected)
