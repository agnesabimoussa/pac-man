import json
import sys
from typing import Any, Dict

from pydantic import ValidationError

from errors.file_errors import FileError
from errors.parsing_errors import (
    InvalidConfigStructure,
    InvalidJsonFormat,
    InvalidSchema,
)
from schemas.game_configuration import GameConfiguration


class Parser:
    """Reads and validates the game's JSON(+comments) configuration file."""

    def __init__(self, config_file: str) -> None:
        """Store the path to the configuration file to parse.

        Args:
            config_file: Path to the JSON configuration file.
        """
        self.config_file = config_file

    def open_config(self) -> Dict[str, Any]:
        """Read the config file and decode it as JSON.

        Strips full-line '#' and '//' comments before decoding.

        Returns:
            The raw, unvalidated configuration as a dict.

        Raises:
            FileError: The file does not exist or cannot be read.
            InvalidJsonFormat: The file content isn't valid JSON.
            InvalidConfigStructure: The JSON is valid but its top level
                isn't an object (e.g. a list or a bare number).
        """
        try:
            with open(self.config_file, "r", encoding="utf-8") as fd:
                raw_text = fd.read()
        except OSError:
            raise FileError(
                "FileError exception occured. "
                f"{self.config_file} does not exist or cannot be read.")

        try:
            data = json.loads(self._strip_comments(raw_text))
        except json.JSONDecodeError as exc:
            raise InvalidJsonFormat(
                "InvalidJsonFormat exception occured. "
                f"Make sure {self.config_file} contains valid JSON "
                f"(after '#'/'//' comment lines are stripped): {exc}")

        if not isinstance(data, dict):
            raise InvalidConfigStructure(
                "InvalidConfigStructure exception occured. "
                f"{self.config_file} must contain a JSON object at the "
                'top level (e.g. { "lives": 3 }).')

        return data

    @staticmethod
    def _strip_comments(text: str) -> str:
        """Remove full-line '#' and '//' comments from raw config text.

        Only lines whose first non-whitespace characters are '#' or '//'
        are dropped; content on the same line as real JSON is left alone.

        Args:
            text: Raw file content.

        Returns:
            The file content with comment-only lines removed.
        """
        kept_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            kept_lines.append(line)
        return "\n".join(kept_lines)

    def parse_config(self) -> GameConfiguration:
        """Validate the raw config into a GameConfiguration.

        Unknown keys are ignored. Any key with a missing or invalid value
        (wrong type or out of range) falls back to its default, with a
        warning logged for each — the whole file is only ever rejected for
        the unrecoverable cases handled in open_config().

        Returns:
            A fully populated, valid GameConfiguration.

        Raises:
            InvalidSchema: Defensive fallback if a valid configuration
                still couldn't be built (should not normally happen, since
                every field has a valid default).
        """
        raw = self.open_config()
        known_fields = set(GameConfiguration.model_fields)

        ignored_keys = sorted(set(raw) - known_fields)
        if ignored_keys:
            self._warn(f"ignoring unknown config key(s): {ignored_keys}.")

        candidate = {key: raw[key] for key in raw if key in known_fields}

        while True:
            try:
                return GameConfiguration(**candidate)
            except ValidationError as exc:
                invalid_fields = {
                    str(error["loc"][0])
                    for error in exc.errors()
                    if error["loc"]
                }
                if not invalid_fields:
                    raise InvalidSchema(
                        "InvalidSchema exception occured. "
                        f"Could not build a valid configuration from "
                        f"{self.config_file}: {exc}")
                for field_name in invalid_fields:
                    self._warn(
                        f"invalid value for '{field_name}' "
                        f"({candidate.get(field_name)!r}); "
                        "falling back to default.")
                    candidate.pop(field_name, None)

    @staticmethod
    def _warn(message: str) -> None:
        """Print a clear, user-friendly warning to stderr.

        Args:
            message: The warning text (without prefix/newline).
        """
        print(f"[config] Warning: {message}", file=sys.stderr)
