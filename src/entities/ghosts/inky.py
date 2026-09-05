import random
from typing import List, Optional

from entities.ghosts.blinky import Blinky
from entities.ghosts.ghost import Ghost
from entities.player import Player
from maze.pathfinding import Cell


class Inky(Ghost):
    """Flanking: mirrors the player's position through Blinky's position.

    Reads as unpredictable since it depends on where Blinky is. Falls
    back to a random tile if no `Blinky` is among `ghosts`.
    """

    def target_tile(
        self,
        maze: List[List[int]],
        player: Player,
        ghosts: List["Ghost"],
    ) -> Cell:
        """Target the player's position reflected through Blinky's."""
        blinky = self._find_blinky(ghosts)
        if blinky is None:
            return self._random_cell(maze)
        blinky_x, blinky_y = blinky.position
        player_x, player_y = player.position
        return (2 * player_x - blinky_x, 2 * player_y - blinky_y)

    @staticmethod
    def _find_blinky(ghosts: List["Ghost"]) -> Optional[Blinky]:
        """Find the `Blinky` instance among `ghosts`, if any."""
        for ghost in ghosts:
            if isinstance(ghost, Blinky):
                return ghost
        return None

    @staticmethod
    def _random_cell(maze: List[List[int]]) -> Cell:
        """Pick a uniformly random cell within the maze's bounds."""
        height = len(maze)
        width = len(maze[0]) if height else 0
        return (random.randrange(width), random.randrange(height))
