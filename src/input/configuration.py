from pydantic import BaseModel, Field


class Configuration(BaseModel):
    highscore_filename: str = Field(default="data/highscores.txt")
    lives: int = Field(default=3)
    points_per_pacgum: int = Field(default=10)
    points_per_super_pacgum: int = Field(default=50)
    points_per_ghost: int = Field(default=200)
    seed: int | None = Field(default=None)
    zones_color: int | None = Field(default="blue")
