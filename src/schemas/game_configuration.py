from pydantic import BaseModel, ConfigDict, Field


class GameConfiguration(BaseModel):
    """Schema for the game's configuration file.

    Every field has a safe fallback default so a
    missing or invalid config value never crashes the game.
    """

    model_config = ConfigDict(extra="ignore")

    highscore_filename: str = Field(
        default="data/highscores.json",
        min_length=1,
        description="Path to the persistent highscore JSON file.")
    width: int = Field(
        default=21,
        ge=5,
        le=101,
        description="Maze width in cells, passed to the maze generator.")
    height: int = Field(
        default=21,
        ge=5,
        le=101,
        description="Maze height in cells, passed to the maze generator.")
    lives: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Starting lives for the player.")
    points_per_pacgum: int = Field(
        default=10,
        ge=0,
        description="Score awarded per pacgum eaten.")
    points_per_super_pacgum: int = Field(
        default=50,
        ge=0,
        description="Score awarded per super-pacgum eaten.")
    points_per_ghost: int = Field(
        default=200,
        ge=0,
        description="Score awarded per edible ghost eaten.")
    seed: int | None = Field(
        default=42,
        description="Fixed seed for level 1's maze; null means random.")
    level_max_time: int = Field(
        default=90,
        ge=10,
        le=3600,
        description="Time limit per level, in seconds.")
    player_speed: float = Field(
        default=4.0,
        gt=0,
        le=20,
        description="Player movement speed, in tiles per second.")
    ghost_speed: float = Field(
        default=3.5,
        gt=0,
        le=20,
        description="Ghost movement speed, in tiles per second.")
