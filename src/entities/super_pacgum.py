from typing import List

from entities.ghosts.ghost import Ghost
from entities.pacgum import Pacgum


class SuperPacgum(Pacgum):
    """A power pellet: a pacgum that also frightens every ghost when eaten."""

    def frighten_ghosts(self, ghosts: List[Ghost]) -> None:
        """Make every ghost edible.

        Args:
            ghosts: Every ghost in the level.
        """
        for ghost in ghosts:
            ghost.frighten()
