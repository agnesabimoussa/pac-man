import json
import sys
from typing import Any

from pydantic import ValidationError

from schemas.highscores import Highscores, Score

MAX_HIGHSCORE_ENTRIES = 10


class HighscoreLoader:
    """Loads the persistent highscore table from disk."""

    def __init__(self, filename: str) -> None:
        """Store the path to the highscore file.

        Args:
            filename: Path to the highscore JSON file.
        """
        self.filename = filename

    def load(self) -> Highscores:
        """Load and validate the highscore table.

        Returns:
            The highscore table, sorted by score descending, capped at
            10 entries.
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

        if len(valid_scores) > MAX_HIGHSCORE_ENTRIES:
            self._warn(
                f"{self.filename} has more than {MAX_HIGHSCORE_ENTRIES} "
                "valid entries; keeping only the top ones.")
            valid_scores = valid_scores[:MAX_HIGHSCORE_ENTRIES]

        try:
            return Highscores(scores=valid_scores)
        except ValidationError:
            return Highscores()

    def save(self, highscores: Highscores) -> None:
        """Persist the highscore table to disk.

        Args:
            highscores: The table to save.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as fd:
                fd.write(highscores.model_dump_json(indent=2))
        except OSError as exc:
            self._warn(f"could not save to {self.filename}: {exc}")

    def record(self, score: Score, highscores: Highscores) -> Highscores:
        """Insert a new score, keep the top entries, and persist the result.

        Args:
            score: The new score to insert.
            highscores: The current highscore table.

        Returns:
            The updated, saved highscore table.
        """
        scores = sorted(
            list(highscores.scores) + [score],
            key=lambda entry: (-entry.score, entry.name),
        )[:MAX_HIGHSCORE_ENTRIES]
        updated = Highscores(scores=scores)
        self.save(updated)
        return updated

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
