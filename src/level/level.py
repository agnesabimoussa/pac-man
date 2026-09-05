from typing import List

from entities.cheat_state import CheatState
from entities.direction import Direction
from entities.ghosts.blinky import Blinky
from entities.ghosts.clyde import Clyde
from entities.ghosts.ghost import Ghost
from entities.ghosts.inky import Inky
from entities.ghosts.pinky import Pinky
from entities.pacgums.pacgum import Pacgum
from entities.player import Player
from entities.pacgums.super_pacgum import SuperPacgum
from maze.pathfinding import Cell, LOGO_CELL, neighbors
from mazegenerator import MazeGenerator
from schemas.game_configuration import GameConfiguration


class Level:
    """Orchestrates one level: ghosts, pacgums, timing, and collisions.

    Attributes:
        level_number: 1-indexed level this instance represents.
        maze: Row-major wall-bitmask grid.
        player: The player entity.
        ghosts: The four ghosts.
        pacgums: Every pacgum and super-pacgum in the maze.
        remaining_time: Seconds left before the level's time limit.
        won: Whether every pacgum has been eaten.
        game_over: Whether the player has run out of lives.
    """

    def __init__(
        self,
        level_number: int,
        maze: List[List[int]],
        player: Player,
        ghosts: List[Ghost],
        pacgums: List[Pacgum],
        max_time: float,
        points_per_ghost: int,
        cheat_state: CheatState,
    ) -> None:
        """Initialize a level with its entities already placed.

        Args:
            level_number: 1-indexed level this instance represents.
            maze: Row-major wall-bitmask grid.
            player: The player entity.
            ghosts: The four ghosts.
            pacgums: Every pacgum and super-pacgum in the maze.
            max_time: Time limit for this level, in seconds.
            points_per_ghost: Points awarded for eating an edible ghost.
            cheat_state: The active cheat toggles/values.
        """
        self.level_number = level_number
        self.maze = maze
        self.player = player
        self.ghosts = ghosts
        self.pacgums = pacgums
        self.max_time = max_time
        self.points_per_ghost = points_per_ghost
        self.cheat_state = cheat_state
        self.remaining_time = max_time
        self.won = False
        self.game_over = False
        self._requested_direction = player.direction
        self._player_move_cooldown = 0.0

    @classmethod
    def create(
        cls,
        level_number: int,
        maze_generator: MazeGenerator,
        player: Player,
        config: GameConfiguration,
        cheat_state: CheatState,
    ) -> "Level":
        """Build a level from a freshly generated maze.

        Args:
            level_number: 1-indexed level to build.
            maze_generator: The generated maze for this level.
            player: The player entity, moved to the maze's center.
            config: The game configuration.
            cheat_state: The active cheat toggles/values.

        Returns:
            A ready-to-play `Level`.
        """
        maze = maze_generator.maze
        height = len(maze)
        width = len(maze[0]) if height else 0
        corners: List[Cell] = [
            (0, 0),
            (width - 1, 0),
            (0, height - 1),
            (width - 1, height - 1),
        ]

        player.move_to((width // 2, height // 2), Direction.EAST)

        ghosts: List[Ghost] = [
            Blinky("Blinky", (255, 0, 0), corners[0],
                   config.ghost_speed, config.frightened_seconds,
                   config.ghost_respawn_seconds),
            Pinky("Pinky", (255, 184, 222), corners[1],
                  config.ghost_speed, config.frightened_seconds,
                  config.ghost_respawn_seconds),
            Inky("Inky", (0, 255, 255), corners[2],
                 config.ghost_speed, config.frightened_seconds,
                 config.ghost_respawn_seconds),
            Clyde("Clyde", (255, 184, 82), corners[3],
                  config.ghost_speed, config.frightened_seconds,
                  config.ghost_respawn_seconds),
        ]

        pacgums: List[Pacgum] = []
        for y in range(height):
            for x in range(width):
                if maze[y][x] == LOGO_CELL:
                    continue
                if (x, y) in corners:
                    pacgums.append(
                        SuperPacgum((x, y), config.points_per_super_pacgum))
                else:
                    pacgums.append(Pacgum((x, y), config.points_per_pacgum))

        return cls(
            level_number, maze, player, ghosts, pacgums,
            config.level_max_time, config.points_per_ghost, cheat_state)

    def update(self, dt: float) -> None:
        """Advance the level by `dt` seconds.

        Args:
            dt: Elapsed seconds since the last update.
        """
        if self.is_complete():
            return

        self._tick_timer(dt)
        if self.is_complete():
            return

        self._move_player(dt)

        if not self.cheat_state.ghosts_frozen:
            for ghost in self.ghosts:
                ghost.update(dt, self.maze, self.player, self.ghosts)

        self._consume_pacgums()
        self._resolve_ghost_collisions()

        if all(pacgum.eaten for pacgum in self.pacgums):
            self.won = True

    def skip(self) -> None:
        """Cheat: immediately win the level."""
        for pacgum in self.pacgums:
            pacgum.eaten = True
        self.won = True

    def set_player_direction(self, direction: Direction) -> None:
        """Queue the direction the player should move towards.

        Args:
            direction: The requested movement direction.
        """
        self._requested_direction = direction

    def is_complete(self) -> bool:
        """Return whether this level has ended, won or lost."""
        return self.won or self.game_over

    def _move_player(self, dt: float) -> None:
        """Step the player towards `_requested_direction`, paced by speed."""
        self._player_move_cooldown -= dt
        if self._player_move_cooldown > 0:
            return
        speed = self.player.speed * self.cheat_state.player_speed_multiplier
        if speed <= 0:
            return
        self._player_move_cooldown += 1.0 / speed

        dx, dy = self._requested_direction.delta
        next_cell = (
            self.player.position[0] + dx, self.player.position[1] + dy)
        if next_cell in neighbors(self.maze, self.player.position):
            self.player.move_to(next_cell, self._requested_direction)
        else:
            self.player.direction = self._requested_direction

    def _tick_timer(self, dt: float) -> None:
        """Count down the level timer, restarting it if it runs out."""
        self.remaining_time -= dt
        if self.remaining_time <= 0:
            self._lose_life()
            self.remaining_time = self.max_time

    def _consume_pacgums(self) -> None:
        """Eat any pacgum the player is standing on."""
        for pacgum in self.pacgums:
            if pacgum.try_consume(self.player) and \
                    isinstance(pacgum, SuperPacgum):
                pacgum.frighten_ghosts(self.ghosts)

    def _resolve_ghost_collisions(self) -> None:
        """Handle the player touching a ghost."""
        for ghost in self.ghosts:
            if ghost.position != self.player.position or ghost.is_eaten():
                continue
            if ghost.is_edible():
                ghost.get_eaten()
                self.player.add_score(self.points_per_ghost)
            else:
                self._lose_life()

    def _lose_life(self) -> None:
        """Remove a life (unless invincible) and respawn or end the game."""
        if self.cheat_state.invincible:
            return
        if self.player.lose_life():
            self.game_over = True
        else:
            height = len(self.maze)
            width = len(self.maze[0]) if height else 0
            self.player.move_to(
                (width // 2, height // 2), Direction.EAST)
