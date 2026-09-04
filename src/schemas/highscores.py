from pydantic import BaseModel, Field


class Score(BaseModel):
    """A single highscore entry.

    Attributes:
        name: Player name, max 10 characters, alphanumeric and spaces only.
        score: Non-negative score value.
    """

    name: str = Field(
        max_length=10,
        pattern=r"^[A-Za-z0-9 ]+$",
        description="Player name (max 10 chars, alphanumeric and spaces).")
    score: int = Field(
        ge=0,
        description="Score value, non-negative.")


class Highscores(BaseModel):
    """The persistent highscore table.

    Attributes:
        scores: Top scores, best first, capped at 10 entries.
    """

    scores: list[Score] = Field(
        default_factory=list,
        max_length=10,
        description="Top 10 highscore entries.")
