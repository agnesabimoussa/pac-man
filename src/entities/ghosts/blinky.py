from typing import List

from entities.ghosts.ghost import Ghost
from entities.player import Player
from maze.pathfinding import Cell


class Blinky(Ghost):
    """Direct chase: always targets the player's current cell."""

    def target_tile(
        self,
        maze: List[List[int]],
        player: Player,
        ghosts: List["Ghost"],
    ) -> Cell:
        """Target the player's current cell."""
        return player.position
