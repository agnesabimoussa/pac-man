class CheatState:
    """Toggleable and adjustable cheats.

    Attributes:
        invincible: Whether ghosts can cost the player a life.
        ghosts_frozen: Whether ghosts are stopped.
        player_speed_multiplier: Multiplies the player's base speed.
    """

    MIN_SPEED_MULTIPLIER = 0.25
    MAX_SPEED_MULTIPLIER = 3.0
    SPEED_STEP = 0.25

    def __init__(self) -> None:
        """Initialize all cheats to their default, off/neutral state."""
        self.invincible = False
        self.ghosts_frozen = False
        self.player_speed_multiplier = 1.0

    def toggle_invincible(self) -> None:
        """Flip invincibility on or off."""
        self.invincible = not self.invincible

    def toggle_ghost_freeze(self) -> None:
        """Flip ghost freeze on or off."""
        self.ghosts_frozen = not self.ghosts_frozen

    def increase_player_speed(self) -> None:
        """Raise the player speed multiplier by one step."""
        self.player_speed_multiplier = min(
            self.MAX_SPEED_MULTIPLIER,
            self.player_speed_multiplier + self.SPEED_STEP)

    def decrease_player_speed(self) -> None:
        """Lower the player speed multiplier by one step."""
        self.player_speed_multiplier = max(
            self.MIN_SPEED_MULTIPLIER,
            self.player_speed_multiplier - self.SPEED_STEP)
