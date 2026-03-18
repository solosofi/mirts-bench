# Polytopia LLM Benchmark

A minimal benchmark harness that turns The Battle of Polytopia into an LLM evaluation loop: game state -> prompt -> LLM action -> apply -> score (ELO).

This repo only contains the game binary, so the benchmark is built as a separate Python package with pluggable adapters. The `manual` adapter works out of the box. The `ui` adapter is a stub that documents where automation hooks go.

## Quick start

Install as a module:

```powershell
pip install polytopia-bench
```

1) Put your turn-by-turn state JSON files in a folder, e.g. `examples/` or `states/`.
2) Run the benchmark:

```powershell
python -m polytopia_bench run --difficulty easy --opponents 1 --games 1 --adapter manual --states-dir examples
```

Or using the console script:

```powershell
polybench run --difficulty easy --opponents 1 --games 1 --adapter manual --states-dir examples
```

3) If you have an LLM command:

```powershell
python -m polytopia_bench run --difficulty hard --opponents 7 --games 1 --adapter manual --states-dir examples --llm-cmd "python examples\echo_llm.py"
```

4) If you want to call an OpenAI-compatible HTTP endpoint:

```powershell
python -m polytopia_bench run --difficulty hard --opponents 7 --games 1 --adapter manual --states-dir examples --llm-host http://localhost:8000 --llm-model your-model --llm-api-key YOUR_KEY
```

Env alternative:

```powershell
$env:POLYBENCH_LLM_HOST = "http://localhost:8000"
$env:POLYBENCH_LLM_MODEL = "your-model"
$env:POLYBENCH_LLM_API_KEY = "YOUR_KEY"
python -m polytopia_bench run --difficulty hard --opponents 7 --games 1 --adapter manual --states-dir examples
```

## Python API

```python
import polybench

cfg = polybench.RunConfig(
    difficulty="easy",
    opponents=1,
    games=1,
    adapter="manual",
    states_dir="examples",
    llm_host="http://localhost:8000",
    llm_model="your-model",
    llm_api_key="YOUR_KEY",
)
polybench.run_benchmark(cfg)
```

## How it works

- Loads a game state (JSON).
- Builds a prompt with a strict action schema.
- Calls the LLM (or mock).
- Parses and validates the JSON action.
- Applies the action (manual = you do it in-game, then press Enter).
- Stops after 30 actions (Perfection mode limit), then computes ELO and writes a summary.

## Inputs

State JSON must include at least:
- `turn`
- `player`
- `cities`
- `units`
- `tech`
- `map`

See `examples/state_example.json` for a template.

## Action schema

Allowed action types:
- `end_turn`
- `move`
- `attack`
- `train`
- `build`
- `research`

The LLM must return JSON only. Required fields per action are enforced by the validator in `polytopia_bench/schema.py`.

## Output

Each run writes:
- `runs/<timestamp>_<difficulty>_<opponents>/game_###/turn_###_prompt.txt`
- `runs/<timestamp>_<difficulty>_<opponents>/game_###/turn_###_response.txt`
- `runs/<timestamp>_<difficulty>_<opponents>/game_###/turn_###_action.json`
- `runs/<timestamp>_<difficulty>_<opponents>/summary.json`

## Options

`python -m polytopia_bench run` supports:
- `--difficulty` easy | normal | hard | crazy
- `--opponents` 1 | 7 | 15
- `--games` (default 1)
- `--adapter` manual | ui
- `--states-dir` (manual only)
- `--llm-cmd` external command that reads prompt on stdin and returns JSON on stdout
- `--llm-host` HTTP base URL (OpenAI-compatible `/v1/chat/completions`)
- `--llm-model` model name for HTTP LLM
- `--llm-api-key` API key for HTTP LLM (or set `POLYBENCH_LLM_API_KEY`)
- `--k-factor` ELO K (default 32)
- `--opponent-elo` (default 1000)
- `--start-elo` (default 1000)

## Notes

- Manual adapter: after each action, you apply it in-game and press Enter.
- UI adapter: placeholder only. It expects a `calibration.json` and is where you would wire automation.
