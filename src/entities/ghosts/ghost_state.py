from enum import Enum


class GhostState(Enum):
    """Lifecycle state of a ghost."""

    CHASING = "chasing"
    FRIGHTENED = "frightened"
    EATEN = "eaten"
