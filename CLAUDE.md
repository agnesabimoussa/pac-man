# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

This is a 42 school project: recreate the arcade game Pac-Man ("Pacman — Ghosts! More ghosts!", subject v1.5 in `inputs/en.subject.pdf`) in Python 3.11, OOP style, done by login `aabi-mou`.

Hard constraints from the subject that shape every design decision here:
- Any graphics library used must be "similar to MLX": every library function called must have a direct MLX (miniLibX) equivalent (window creation, image load/blit, pixel put/get, key/mouse/loop hooks, basic string draw). No shape-drawing, no audio, no sprite/collision helpers, no widgets — those must be hand-rolled if needed. Verify any new pygame/graphics call against this before using it.
- The app must never crash / show a traceback to the user. Top-level code should catch and print a clean message. Bad config values must be clamped to safe defaults and unknown keys ignored — not treated as fatal.
- The maze package (`mazegenerator`, bundled as `inputs/mazegenerator-2.1.0-py3-none-any.whl`) is externally assigned and must not be modified — only consumed through its public API.
- Config files are JSON that also allow `#`-comment lines, which must be stripped before `json.load`.
- Code must include type hints for function parameters, return types, and variables where applicable (using the typing module).
- Include docstrings in functions and classes following PEP 257 Google style to document purpose, parameters, and returns.
- Pygame is the user's graphics library of choice to be implemented.

## Commands

Dependency management is via `uv`.

```sh
make install       # uv venv && uv sync
make run            # uv run python3 src/pac-man.py inputs/config.json
make debug           # same, under pdb
make lint             # flake8 src/. && mypy src/.
make lint-strict       # flake8 + a stricter mypy invocation
make clean               # remove __pycache__, .mypy_cache, .pytest_cache
```

Run directly with a different config file:
```sh
uv run python3 src/pac-man.py path/to/config.json
```

Lint config lives in `.flake8` and `mypy.ini` (mypy: `warn_return_any`, `warn_unused_ignores`, `disallow_untyped_defs`, `check_untyped_defs`, `ignore_missing_imports`, pydantic plugin enabled). There is no test suite yet.

Note: `make lint-strict`'s mypy flags are currently concatenated without spaces (`--warn-return-any--warn-unused-ignores`, `--disallow-untyped-defs--check-untyped-defs`) and will not parse correctly as written.

## Architecture

The entry point is `src/pac-man.py` (`main()`), which takes exactly one CLI argument (path to a config JSON file), and on any exception prints it and exits cleanly rather than propagating a traceback.

Config loading is a two-stage pipeline in `src/parser.py` (`Parser` class):
1. `open_config()` reads and JSON-decodes the file, raising `FileError` (`src/errors/file_errors.py`) if the file is missing, or `InvalidJsonFormat` (`src/errors/parsing_errors.py`) if it isn't valid JSON.
2. `parse_config()` validates the parsed dict against the `Configuration` pydantic model (`src/input/configuration.py`) via `TypeAdapter`, raising `InvalidSchema` on a `ValidationError`.

`Configuration` (`src/input/configuration.py`) is a pydantic `BaseModel` defining every recognized config key with a default (`highscore_filename`, `lives`, `points_per_pacgum`, `points_per_super_pacgum`, `points_per_ghost`, `seed`, `zones_color`). This model is the single source of truth for what config keys exist and their defaults — new config keys (e.g. per-level `width`/`height`, `pacgum` count, `level_max_time`) should be added here first.

Custom exceptions are split by concern: `src/errors/file_errors.py` for file/argument problems, `src/errors/parsing_errors.py` for JSON/schema problems. Both follow the same pattern — a `message` constructor arg with a default string, calling `super().__init__(self.message)`.

Everything beyond config parsing — maze integration, rendering, game loop, entities (player/ghosts/pacgums), menus/HUD, highscores, cheat mode — is not yet implemented.

### `mazegenerator` package (assigned, read-only dependency)

```python
from mazegenerator import MazeGenerator
mg = MazeGenerator(size=(width, height), entry_cell=(x, y), exit_cell=(x, y), perfect=False, seed=42)
mg.maze          # list[list[int]], row-major [y][x], each cell a 4-bit wall mask
mg.maze_entry    # (x, y)
mg.maze_exit     # (x, y)
mg.shortest_path # str of 'N'/'E'/'S'/'W', entry->exit, or False if none
mg.generate(seed=0)  # regenerate in place
```

Wall bit encoding per cell (bit set = wall present, blocking movement that direction): bit0(1)=North, bit1(2)=East, bit2(4)=South, bit3(8)=West. A cell value of exactly `15` is a decorative embedded "42" logo cell, walled on all sides — treat as a solid obstacle, not a normal corridor cell. `perfect=False` (required by the subject) makes the generator braid the maze to remove dead ends, producing loops suitable for ghost-chase gameplay.
