import json
import sys
from typing import Any

from pydantic import ValidationError

from schemas.highscores import Highscores, Score


class HighscoreLoader:
    """Loads the persistent highscore table from disk.

    Never raises for file-shaped problems (missing file, invalid JSON,
    invalid entries) — those are all recoverable per subject §V.5, so
    `load()` always returns a usable `Highscores`, falling back to an
    empty one and logging a warning as needed.
    """

    def __init__(self, filename: str) -> None:
        """Store the path to the highscore file.

        Args:
            filename: Path to the highscore JSON file.
        """
        self.filename = filename

    def load(self) -> Highscores:
        """Load and validate the highscore table.

        A missing file means there are no highscores at all yet (not an
        error). Invalid JSON, a wrong top-level shape, or individually
        invalid entries are logged and skipped rather than failing the
        whole load. If fewer than 10 valid entries are found, exactly
        those are returned — the result is never padded.

        Returns:
            The highscore table, sorted by score (descending, ties broken
            alphabetically by name), capped at 10 entries.
        """
        try:
            with open(self.filename, "r", encoding="utf-8") as fd:
                raw_text = fd.read()
        except OSError:
            return Highscores()

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            self._warn(
                f"{self.filename} is not valid JSON ({exc}); "
                "starting with an empty highscore table.")
            return Highscores()

        if not isinstance(data, dict) or not isinstance(
                data.get("scores"), list):
            self._warn(
                f"{self.filename} must contain a JSON object with a "
                '"scores" list; starting with an empty highscore table.')
            return Highscores()

        valid_scores = self._parse_entries(data["scores"])
        valid_scores.sort(key=lambda entry: (-entry.score, entry.name))

        if len(valid_scores) > 10:
            self._warn(
                f"{self.filename} has more than 10 valid entries; "
                "keeping only the top 10.")
            valid_scores = valid_scores[:10]

        try:
            return Highscores(scores=valid_scores)
        except ValidationError:
            return Highscores()

    def _parse_entries(self, raw_entries: list[Any]) -> list[Score]:
        """Validate each raw entry on its own, dropping invalid ones.

        Args:
            raw_entries: The raw `scores` list decoded from JSON.

        Returns:
            Only the entries that validated as a `Score`.
        """
        valid_scores = []
        for index, raw_entry in enumerate(raw_entries):
            if not isinstance(raw_entry, dict):
                self._warn(
                    f"dropping highscore entry at index {index}: "
                    f"not an object ({raw_entry!r}).")
                continue
            try:
                valid_scores.append(Score(**raw_entry))
            except ValidationError as exc:
                self._warn(
                    f"dropping invalid highscore entry at index {index} "
                    f"({raw_entry!r}): {exc}")
        return valid_scores

    @staticmethod
    def _warn(message: str) -> None:
        """Print a clear, user-friendly warning to stderr.

        Args:
            message: The warning text (without prefix/newline).
        """
        print(f"[highscore] Warning: {message}", file=sys.stderr)
