from enum import Enum
from typing import Tuple


class Direction(Enum):
    """A movement direction on the 2D maze grid."""

    NORTH = (0, -1)
    EAST = (1, 0)
    SOUTH = (0, 1)
    WEST = (-1, 0)

    @property
    def delta(self) -> Tuple[int, int]:
        """Return the (dx, dy) offset this direction moves by."""
        return self.value
