from typing import Tuple

from entities.player import Player


class Pacgum:
    """A collectible dot placed in a maze corridor.

    Attributes:
        position: The (x, y) cell this pacgum occupies.
        points: Points awarded when eaten.
        eaten: Whether it has been eaten.
    """

    def __init__(self, position: Tuple[int, int], points: int) -> None:
        """Initialize an uneaten pacgum.

        Args:
            position: The (x, y) cell this pacgum occupies.
            points: Points awarded when eaten.
        """
        self.position = position
        self.points = points
        self.eaten = False

    def try_consume(self, player: Player) -> bool:
        """Eat this pacgum if the player is standing on it.

        Args:
            player: The player entity.

        Returns:
            True if it was eaten just now.
        """
        if self.eaten or player.position != self.position:
            return False
        self.eaten = True
        player.add_score(self.points)
        return True
