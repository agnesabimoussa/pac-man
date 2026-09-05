from typing import List

from entities.ghosts.ghost import Ghost
from entities.player import Player
from maze.pathfinding import Cell

CLYDE_SHY_DISTANCE = 8


class Clyde(Ghost):
    """Shy: chases directly from afar, but scatters home once close."""

    def target_tile(
        self,
        maze: List[List[int]],
        player: Player,
        ghosts: List["Ghost"],
    ) -> Cell:
        """Target the player if far away, otherwise retreat home."""
        player_x, player_y = player.position
        x, y = self.position
        distance = abs(player_x - x) + abs(player_y - y)
        if distance > CLYDE_SHY_DISTANCE:
            return player.position
        return self.home_corner
