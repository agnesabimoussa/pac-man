import re
import sys
import time
from typing import Tuple

from entities.direction import Direction
from schemas.highscores import Highscores, Score

NAME_PATTERN = re.compile(r"^[A-Za-z0-9 ]+$")
NAME_MAX_LENGTH = 10
DEFAULT_NAME = "PLAYER"
MAX_HIGHSCORE_ENTRIES = 10


class Player:
    """Tracks the human player's live state for one game session.

    The player's name is unknown at game start (classic arcade flow: it's
    only entered at game over, and only if the score makes the top 10),
    so `name` starts empty and is set later via `set_name()`.

    Attributes:
        name: Player name, entered at game over and saved to highscores.
        lives: Remaining lives.
        score: Accumulated score.
        position: Current (x, y) cell in the maze.
        direction: Current facing direction, updated on every move (also
            used by ghosts, e.g. Pinky's ambush targeting).
    """

    def __init__(self, lives: int) -> None:
        """Initialize a new player at the start of a game.

        Args:
            lives: Starting number of lives, typically `config.lives`.
        """
        self.name = ""
        self.lives = lives
        self.score = 0
        self.position: Tuple[int, int] = (0, 0)
        self.direction = Direction.EAST
        self._start_time = time.monotonic()

    def move_to(
            self, position: Tuple[int, int], direction: Direction) -> None:
        """Update the player's position and facing direction.

        Args:
            position: The player's new (x, y) cell.
            direction: The direction just moved in.
        """
        self.position = position
        self.direction = direction

    def set_name(self, name: str) -> None:
        """Set the player's name, entered at game over.

        Args:
            name: Candidate name. Falls back to `DEFAULT_NAME` if it
                doesn't satisfy the highscore naming rules (max 10
                characters, alphanumeric and spaces only).
        """
        self.name = self._validate_name(name)

    def add_score(self, points: int) -> None:
        """Add points to the player's score.

        Args:
            points: Points to add; ignored if not positive.
        """
        if points > 0:
            self.score += points

    def lose_life(self) -> bool:
        """Remove one life from the player.

        Returns:
            True if the player has no lives left (game over).
        """
        self.lives = max(0, self.lives - 1)
        return self.is_game_over()

    def is_game_over(self) -> bool:
        """Return whether the player has run out of lives."""
        return self.lives <= 0

    def elapsed_seconds(self) -> float:
        """Return the time elapsed since this player's game started."""
        return time.monotonic() - self._start_time

    def to_score(self) -> Score:
        """Convert the player's current score into a highscore entry.

        Returns:
            A `Score` with this player's name and score.
        """
        return Score(name=self.name, score=self.score)

    def qualifies_for_highscore(self, highscores: Highscores) -> bool:
        """Return whether this player's score belongs on the top 10.

        Args:
            highscores: The current highscore table.

        Returns:
            True if the table isn't full yet, or if this score beats
            its current lowest entry.
        """
        if len(highscores.scores) < MAX_HIGHSCORE_ENTRIES:
            return True
        lowest_score: int = min(
            entry.score for entry in highscores.scores)
        return self.score > lowest_score

    @staticmethod
    def _validate_name(name: str) -> str:
        """Sanitize a candidate player name against highscore rules.

        Args:
            name: Raw candidate name.

        Returns:
            `name` unchanged if it satisfies the naming rules, otherwise
            `DEFAULT_NAME`.
        """
        if isinstance(name, str) and 1 <= len(name) <= NAME_MAX_LENGTH \
                and NAME_PATTERN.match(name):
            return name
        print(
            f"[player] Warning: invalid player name {name!r}; "
            f"falling back to {DEFAULT_NAME!r}.",
            file=sys.stderr)
        return DEFAULT_NAME
