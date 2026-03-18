import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .adapters import ManualAdapter, UIAutomationAdapter
from .elo import update_elo
from .llm import CommandLLM, HttpLLM, MockLLM
from .prompt import render_prompt
from .schema import parse_action, validate_state

MAX_TURNS = 30


@dataclass
class RunConfig:
    difficulty: str
    opponents: int
    games: int = 1
    adapter: str = "manual"
    states_dir: Optional[str] = None
    llm_cmd: Optional[List[str]] = None
    llm_host: Optional[str] = None
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    k_factor: float = 32.0
    opponent_elo: float = 1000.0
    start_elo: float = 1000.0


def _create_adapter(config: RunConfig):
    if config.adapter == "manual":
        if not config.states_dir:
            raise ValueError("--states-dir is required for manual adapter")
        return ManualAdapter(config.states_dir)
    if config.adapter == "ui":
        return UIAutomationAdapter()
    raise ValueError(f"Unknown adapter: {config.adapter}")


def _create_llm(config: RunConfig):
    if config.llm_cmd:
        return CommandLLM(config.llm_cmd)
    if config.llm_host or config.llm_model or config.llm_api_key:
        if not config.llm_host or not config.llm_model:
            raise ValueError("--llm-host and --llm-model are required for HTTP LLM")
        return HttpLLM(config.llm_host, config.llm_model, config.llm_api_key)
    return MockLLM()


def _run_dir_name(difficulty: str, opponents: int) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{stamp}_{difficulty}_{opponents}"


def run_benchmark(config: RunConfig) -> Dict[str, Any]:
    run_root = Path("runs") / _run_dir_name(config.difficulty, config.opponents)
    run_root.mkdir(parents=True, exist_ok=False)

    adapter = _create_adapter(config)
    llm = _create_llm(config)

    current_elo = float(config.start_elo)
    results: List[Dict[str, Any]] = []

    for game_index in range(1, config.games + 1):
        adapter.reset(config.difficulty, config.opponents, game_index)
        game_dir = run_root / f"game_{game_index:03d}"
        game_dir.mkdir(parents=True, exist_ok=False)

        turn_index = 1
        while not adapter.is_done() and turn_index <= MAX_TURNS:
            state = adapter.get_state()
            validate_state(state)

            prompt = render_prompt(state)
            (game_dir / f"turn_{turn_index:03d}_prompt.txt").write_text(
                prompt, encoding="utf-8"
            )

            response = llm.generate(prompt)
            (game_dir / f"turn_{turn_index:03d}_response.txt").write_text(
                response, encoding="utf-8"
            )

            action = parse_action(response)
            (game_dir / f"turn_{turn_index:03d}_action.json").write_text(
                json.dumps(action, indent=2), encoding="utf-8"
            )

            adapter.apply_action(action, str(game_dir), turn_index)
            turn_index += 1

        max_turns_reached = turn_index > MAX_TURNS and not adapter.is_done()
        if max_turns_reached:
            print(f"Max turns reached ({MAX_TURNS}). Ending game early.")

        result = adapter.get_result()
        result_value = result.get("result")
        if result_value not in {"win", "draw", "loss"}:
            raise ValueError("Adapter result must include result=win/draw/loss")

        elo_before = current_elo
        current_elo = update_elo(
            current_elo, config.opponent_elo, result_value, config.k_factor
        )

        record = {
            "game": game_index,
            "turns": turn_index - 1,
            "max_turns": MAX_TURNS,
            "max_turns_reached": max_turns_reached,
            "result": result_value,
            "score": result.get("score"),
            "elo_before": elo_before,
            "elo_after": current_elo,
        }
        results.append(record)

        print(
            f"Game {game_index}: result={result_value} score={record['score']} "
            f"elo={record['elo_after']:.2f}"
        )

    summary = {
        "difficulty": config.difficulty,
        "opponents": config.opponents,
        "games": config.games,
        "max_turns": MAX_TURNS,
        "k_factor": config.k_factor,
        "opponent_elo": config.opponent_elo,
        "start_elo": config.start_elo,
        "final_elo": current_elo,
        "results": results,
    }

    (run_root / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    print(f"Final ELO: {current_elo:.2f}")
    print(f"Run saved to: {run_root}")

    return summary
