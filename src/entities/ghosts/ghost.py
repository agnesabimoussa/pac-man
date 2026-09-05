from abc import ABC, abstractmethod
from typing import List, Tuple

from entities.direction import Direction
from entities.ghosts.ghost_state import GhostState
from entities.player import Player
from maze.pathfinding import Cell, farthest_cell_from, next_step_towards


class Ghost(ABC):
    """Base class for a ghost moving autonomously through the maze.

    Movement, state transitions, and fleeing are shared by every ghost.
    Subclasses only implement `target_tile()`, which selects the cell to
    chase while `CHASING` — that's the one thing that differs between
    them.

    Attributes:
        name: Display name (e.g. "Blinky").
        color: RGB color used for rendering.
        home_corner: Spawn cell, and respawn target once eaten.
        position: Current (x, y) cell.
        direction: Current facing direction.
        speed: Movement speed, in tiles per second.
        state: Current lifecycle state.
    """

    def __init__(
        self,
        name: str,
        color: Tuple[int, int, int],
        home_corner: Cell,
        speed: float,
        frightened_seconds: float,
        respawn_seconds: float,
    ) -> None:
        """Initialize a ghost at its home corner, chasing by default.

        Args:
            name: Display name (e.g. "Blinky").
            color: RGB color used for rendering.
            home_corner: Spawn cell, and respawn target once eaten.
            speed: Movement speed, in tiles per second.
            frightened_seconds: How long `FRIGHTENED` lasts once
                triggered (`config.frightened_seconds`).
            respawn_seconds: How long `EATEN` lasts before respawning
                (`config.ghost_respawn_seconds`).
        """
        self.name = name
        self.color = color
        self.home_corner = home_corner
        self.speed = speed
        self.frightened_seconds = frightened_seconds
        self.respawn_seconds = respawn_seconds
        self.direction = Direction.EAST
        self.position = home_corner
        self.state = GhostState.CHASING
        self._state_timer = 0.0

    def reset(self) -> None:
        """Place the ghost back at its home corner, chasing again."""
        self.position = self.home_corner
        self.state = GhostState.CHASING
        self._state_timer = 0.0

    def frighten(self) -> None:
        """Make the ghost edible, e.g. after a super-pacgum is eaten.

        No effect if the ghost is already `EATEN` — its eyes returning
        home can't be scared.
        """
        if self.state is GhostState.EATEN:
            return
        self.state = GhostState.FRIGHTENED
        self._state_timer = self.frightened_seconds

    def get_eaten(self) -> None:
        """Transition to `EATEN` after being caught while frightened."""
        self.state = GhostState.EATEN
        self._state_timer = self.respawn_seconds

    def is_edible(self) -> bool:
        """Return whether the ghost can currently be eaten."""
        return self.state is GhostState.FRIGHTENED

    def is_eaten(self) -> bool:
        """Return whether the ghost is eaten (eyes en route home)."""
        return self.state is GhostState.EATEN

    def update(
        self,
        dt: float,
        maze: List[List[int]],
        player: Player,
        ghosts: List["Ghost"],
    ) -> None:
        """Advance the ghost's state and move it one step towards its target.

        Args:
            dt: Elapsed seconds since the last update.
            maze: Row-major wall-bitmask grid of the current level.
            player: The player entity, used as the chase/flee reference.
            ghosts: Every ghost in the level (Inky needs Blinky's cell).
        """
        self._tick_state(dt)

        if self.state is GhostState.CHASING:
            target = self.target_tile(maze, player, ghosts)
        elif self.state is GhostState.FRIGHTENED:
            target = farthest_cell_from(maze, self.position, player.position)
        else:
            target = self.home_corner

        next_cell = next_step_towards(maze, self.position, target)
        if next_cell != self.position:
            self.direction = self._direction_towards(next_cell)
            self.position = next_cell

    @abstractmethod
    def target_tile(
        self,
        maze: List[List[int]],
        player: Player,
        ghosts: List["Ghost"],
    ) -> Cell:
        """Select the cell to chase while in `GhostState.CHASING`.

        Args:
            maze: Row-major wall-bitmask grid of the current level.
            player: The player entity to chase.
            ghosts: Every ghost in the level.

        Returns:
            The (x, y) cell this ghost should path towards. It doesn't
            need to be reachable or in bounds — pathfinding falls back
            to standing still if it isn't.
        """
        raise NotImplementedError

    def _tick_state(self, dt: float) -> None:
        """Count down the state timer, applying it once it runs out."""
        if self.state is GhostState.CHASING:
            return
        self._state_timer -= dt
        if self._state_timer <= 0:
            if self.state is GhostState.EATEN:
                self.reset()
            else:
                self.state = GhostState.CHASING

    def _direction_towards(self, next_cell: Cell) -> Direction:
        """Return the Direction that moves from `position` to `next_cell`."""
        dx = next_cell[0] - self.position[0]
        dy = next_cell[1] - self.position[1]
        for direction in Direction:
            if direction.delta == (dx, dy):
                return direction
        return self.direction
