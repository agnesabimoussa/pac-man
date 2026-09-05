from typing import List

from entities.ghosts.ghost import Ghost
from entities.player import Player
from maze.pathfinding import Cell

AMBUSH_TILES_AHEAD = 4


class Pinky(Ghost):
    """Ambush: targets a few tiles ahead of the player, cutting them off."""

    def target_tile(
        self,
        maze: List[List[int]],
        player: Player,
        ghosts: List["Ghost"],
    ) -> Cell:
        """Target a point `AMBUSH_TILES_AHEAD` cells past the player."""
        dx, dy = player.direction.delta
        x, y = player.position
        return (x + dx * AMBUSH_TILES_AHEAD, y + dy * AMBUSH_TILES_AHEAD)
