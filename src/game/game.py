from entities.cheat_state import CheatState
from entities.direction import Direction
from entities.player import Player
from level.level import Level
from maze.loader import MazeLoader
from schemas.game_configuration import GameConfiguration


class Game:
    """Orchestrates progression across levels for one game session.

    Attributes:
        player: The player entity, persists across levels.
        cheat_state: The active cheat toggles/values.
        current_level: The currently active `Level`.
        victory: Whether every level has been completed.
    """

    def __init__(
        self,
        config: GameConfiguration,
        maze_loader: MazeLoader,
        player: Player,
        cheat_state: CheatState,
    ) -> None:
        """Initialize a game session and build its first level.

        Args:
            config: The game configuration.
            maze_loader: Generates each level's maze.
            player: The player entity.
            cheat_state: The active cheat toggles/values.
        """
        self.config = config
        self.maze_loader = maze_loader
        self.player = player
        self.cheat_state = cheat_state
        self.victory = False
        self._level_number = 1
        self.current_level = self._build_level(self._level_number)

    def update(self, dt: float) -> None:
        """Advance the current level, progressing on a win.

        Args:
            dt: Elapsed seconds since the last update.
        """
        if self.is_over():
            return
        self.current_level.update(dt)
        if self.current_level.won:
            self._advance_level()

    def set_player_direction(self, direction: Direction) -> None:
        """Queue the direction the player should move towards.

        Args:
            direction: The requested movement direction.
        """
        self.current_level.set_player_direction(direction)

    def skip_level(self) -> None:
        """Cheat: immediately win the current level."""
        self.current_level.skip()

    def is_game_over(self) -> bool:
        """Return whether the player has run out of lives."""
        return self.current_level.game_over

    def is_victory(self) -> bool:
        """Return whether every level has been completed."""
        return self.victory

    def is_over(self) -> bool:
        """Return whether the game has ended, won or lost."""
        return self.is_game_over() or self.victory

    def _advance_level(self) -> None:
        """Move to the next level, or declare victory past the last one."""
        if self._level_number >= self.maze_loader.level_count:
            self.victory = True
            return
        self._level_number += 1
        self.current_level = self._build_level(self._level_number)

    def _build_level(self, level_number: int) -> Level:
        """Generate a maze and build the `Level` for it.

        Args:
            level_number: 1-indexed level to build.

        Returns:
            A ready-to-play `Level`.
        """
        maze_generator = self.maze_loader.generate_level(level_number)
        return Level.create(
            level_number, maze_generator, self.player, self.config,
            self.cheat_state)
