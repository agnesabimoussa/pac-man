*This project has been created as part of the 42 curriculum by aabi-mou and miissa.*

# Description

# Instructions

# Resources

# Configuration

The game is launched with a single argument: the path to a JSON configuration
file (`python3 src/pac-man.py path/to/config.json`).

## Format

Standard JSON, with comment support. Comments must be the first
non-whitespace token on their line (inline/trailing comments after real JSON
content are not stripped):
- `# ...`
- `// ...`

## Error handling

- **Unknown keys are ignored.**
- **Missing or invalid values** (wrong type, or out of the range below) **fall
  back to that key's default**, with a warning logged — the game never
  crashes or raises on a bad config value.
- A missing file, a file that isn't valid JSON at all, or JSON whose top
  level isn't an object are the only cases treated as a hard error.

## Keys

| Key | Type | Default | Notes |
|---|---|---|---|
| `highscore_filename` | string | `"data/highscores.json"` | Path to the persistent highscore file. |
| `width` | int | `21` | Maze width in cells. Range `[5, 101]`. |
| `height` | int | `21` | Maze height in cells. Range `[5, 101]`. |
| `levels` | int | `10` | Number of levels. Range `[1, 100]`. |
| `lives` | int | `3` | Starting lives. Range `[1, 10]`. |
| `points_per_pacgum` | int | `10` | Score per pacgum eaten. Non-negative. |
| `points_per_super_pacgum` | int | `50` | Score per super-pacgum eaten. Non-negative. |
| `points_per_ghost` | int | `200` | Score per edible ghost eaten. Non-negative. |
| `seed` | int or `null` | `0` | Fixed seed for level 1's maze; `0` (default) or `null` means level 1 is random too. Later levels are always random. |
| `level_max_time` | int | `90` | Time limit per level, in seconds. Range `[10, 3600]`. |
| `player_speed` | float | `4.0` | Player movement speed, tiles per second. Range `(0, 20]`. |
| `ghost_speed` | float | `3.5` | Ghost movement speed, tiles per second. Range `(0, 20]`. |

## Example

```json
// Example configuration file:
{
    # highscore storage
    "highscore_filename": "data/highscores.json",

    // maze size for level 1 (later levels are generated independently)
    "width": 21,
    "height": 21,
    "seed": 42,
    "levels": 10,

    "lives": 3,
    "level_max_time": 90,

    # scoring
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,

    // movement
    "player_speed": 4.0,
    "ghost_speed": 3.5
}
```

# Highscore

A persistent, file-based highscore table.

## Storage

Stored on disk as a JSON file, at the path given by the config key
`highscore_filename` (default `data/highscores.json`).

## Format

A JSON object holding a list of score entries, validated by the `Score`
and `Highscores` pydantic classes (`src/schemas/highscores.py`):

```json
{
    "scores": [
        {"name": "AGNES", "score": 4200},
        {"name": "MIISSA", "score": 3150},
        {"name": "BOB", "score": 900}
    ]
}
```

- `name`: max 10 characters, alphanumeric and spaces only.
- `score`: a non-negative integer.
- The list holds at most 10 entries.
- Entries are list items rather than dict keys, so the **same name can
  appear more than once** — each completed game that makes the top 10 is
  its own entry, not a "best score per player" record. Submitting a name
  that already exists never merges with or overwrites an existing entry.
- Entries are sorted by score (descending), ties broken alphabetically by
  name.

## Error handling

Never crashes on a bad highscore file:
- A **missing file** just means there are no highscores yet — not an
  error, no warning.
- **Invalid JSON**, or a top level that isn't `{"scores": [...]}`, falls
  back to an empty table with a warning logged.
- Each entry is validated **individually** — a single bad entry (invalid
  name, negative score, wrong type) is dropped with a warning, and loading
  continues with the rest, rather than discarding the whole file.
- If the file happens to hold fewer than 10 valid entries, exactly those
  are returned (never padded); if it somehow holds more than 10, only the
  top 10 by score are kept.

# Maze Generation

# Implementation

# Software Architecture

# Project Management
