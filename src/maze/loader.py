from mazegenerator import MazeGenerator

from errors.maze_errors import MazeGenerationError


class MazeLoader:
    """Generates one maze per game level using the assigned MazeGenerator.

    Level 1 uses a fixed seed and every subsequent level is generated randomly.
    """

    def __init__(
        self,
        width: int,
        height: int,
        level_count: int,
        seed: int | None,
        perfect: bool = False,
        entry_cell: tuple[int, int] = (0, 0),
        exit_cell: tuple[int, int] = (-1, -1),
        random_seed_marker: int = 0,
    ) -> None:
        """Store maze parameters shared by every level.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            level_count: Total number of levels in the game.
            seed: Fixed seed for level 1; a value <= `random_seed_marker`
                (or `None`) means level 1 is random too.
            perfect: Passed through to `MazeGenerator`.
            entry_cell: Passed through to `MazeGenerator`.
            exit_cell: Passed through to `MazeGenerator`.
            random_seed_marker: The seed value that means "random".
        """
        self.width = width
        self.height = height
        self.level_count = level_count
        self.seed = seed
        self.perfect = perfect
        self.entry_cell = entry_cell
        self.exit_cell = exit_cell
        self.random_seed_marker = random_seed_marker

    def generate_level(self, level_number: int) -> MazeGenerator:
        """Generate the maze for a given level.

        Args:
            level_number: 1-indexed level to generate a maze for.

        Returns:
            A freshly generated `MazeGenerator` instance.

        Raises:
            ValueError: `level_number` is outside `[1, level_count]`.
            MazeGenerationError: The underlying library failed to
                generate a maze.
        """
        if not 1 <= level_number <= self.level_count:
            raise ValueError(
                f"level_number must be between 1 and {self.level_count}, "
                f"got {level_number}.")

        resolved_seed = self._resolve_seed(level_number)
        try:
            return MazeGenerator(
                size=(self.width, self.height),
                perfect=self.perfect,
                entry_cell=self.entry_cell,
                exit_cell=self.exit_cell,
                seed=resolved_seed,
            )
        except Exception as exc:
            raise MazeGenerationError(
                "MazeGenerationError exception occured. "
                f"Failed to generate the maze for level {level_number} "
                f"({self.width}x{self.height}, seed={resolved_seed}): "
                f"{exc}") from exc

    def _resolve_seed(self, level_number: int) -> int:
        """Resolve the seed to pass to `MazeGenerator` for a level.

        Args:
            level_number: 1-indexed level being generated.

        Returns:
            `self.seed` for level 1 if it's a usable fixed seed, otherwise
            `self.random_seed_marker` for every other level.
        """
        if level_number == 1 and self.seed is not None \
                and self.seed > self.random_seed_marker:
            return self.seed
        return self.random_seed_marker
