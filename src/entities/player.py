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
    """The human player's live state for one game session.

    Attributes:
        name: Player name.
        lives: Remaining lives.
        score: Accumulated score.
        position: Current (x, y) cell in the maze.
        direction: Current facing direction.
        speed: Base movement speed, in tiles per second.
    """

    def __init__(self, lives: int, speed: float) -> None:
        """Initialize a new player.

        Args:
            lives: Starting number of lives.
            speed: Base movement speed.
        """
        self.name = ""
        self.lives = lives
        self.score = 0
        self.position: Tuple[int, int] = (0, 0)
        self.direction = Direction.EAST
        self.speed = speed
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
        """Set the player's name.

        Args:
            name: Candidate name.
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
            True if the player has no lives left.
        """
        self.lives = max(0, self.lives - 1)
        return self.is_game_over()

    def add_life(self, count: int = 1) -> None:
        """Add extra lives to the player.

        Args:
            count: Number of lives to add.
        """
        if count > 0:
            self.lives += count

    def is_game_over(self) -> bool:
        """Return whether the player has run out of lives."""
        return self.lives <= 0

    def elapsed_seconds(self) -> float:
        """Return the time elapsed since this player's game started."""
        return time.monotonic() - self._start_time

    def to_score(self) -> Score:
        """Convert to a highscore entry.

        Returns:
            A `Score` with this player's name and score.
        """
        return Score(name=self.name, score=self.score)

    def qualifies_for_highscore(self, highscores: Highscores) -> bool:
        """Return whether this player's score belongs on the top 10.

        Args:
            highscores: The current highscore table.

        Returns:
            True if it qualifies.
        """
        if len(highscores.scores) < MAX_HIGHSCORE_ENTRIES:
            return True
        lowest_score: int = min(
            entry.score for entry in highscores.scores)
        return self.score > lowest_score

    @staticmethod
    def _validate_name(name: str) -> str:
        """Sanitize a candidate player name.

        Args:
            name: Raw candidate name.

        Returns:
            `name` if valid, otherwise `DEFAULT_NAME`.
        """
        if isinstance(name, str) and 1 <= len(name) <= NAME_MAX_LENGTH \
                and NAME_PATTERN.match(name):
            return name
        print(
            f"[player] Warning: invalid player name {name!r}; "
            f"falling back to {DEFAULT_NAME!r}.",
            file=sys.stderr)
        return DEFAULT_NAME
