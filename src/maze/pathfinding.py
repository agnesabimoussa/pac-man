from collections import deque
from typing import Deque, Dict, List, Tuple

Cell = Tuple[int, int]

NORTH_WALL = 1
EAST_WALL = 2
SOUTH_WALL = 4
WEST_WALL = 8
LOGO_CELL = 15


def neighbors(maze: List[List[int]], cell: Cell) -> List[Cell]:
    """List the cells reachable from `cell` in a single step.

    Args:
        maze: Row-major wall-bitmask grid ([y][x]) as produced by
            `MazeGenerator` (bit0=North, bit1=East, bit2=South, bit3=West).
        cell: The (x, y) cell to look around.

    Returns:
        Adjacent (x, y) cells not blocked by a wall, within the maze
        bounds, and not a solid "42" logo cell (mask 15).
    """
    height = len(maze)
    width = len(maze[0]) if height else 0
    x, y = cell
    if not (0 <= x < width and 0 <= y < height):
        return []

    walls = maze[y][x]
    candidates = (
        (NORTH_WALL, (x, y - 1)),
        (EAST_WALL, (x + 1, y)),
        (SOUTH_WALL, (x, y + 1)),
        (WEST_WALL, (x - 1, y)),
    )
    reachable = []
    for wall_bit, (nx, ny) in candidates:
        if walls & wall_bit:
            continue
        if not (0 <= nx < width and 0 <= ny < height):
            continue
        if maze[ny][nx] == LOGO_CELL:
            continue
        reachable.append((nx, ny))
    return reachable


def bfs_distances(maze: List[List[int]], start: Cell) -> Dict[Cell, int]:
    """Compute shortest-path distances from `start` to every reachable cell.

    Args:
        maze: Row-major wall-bitmask grid.
        start: The (x, y) cell to search from.

    Returns:
        A mapping of reachable (x, y) cells to their distance from
        `start` (0 for `start` itself), or an empty mapping if `start`
        is outside the maze bounds.
    """
    if not _in_bounds(maze, start):
        return {}

    distances: Dict[Cell, int] = {start: 0}
    queue: Deque[Cell] = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in neighbors(maze, current):
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    return distances


def next_step_towards(maze: List[List[int]], start: Cell, goal: Cell) -> Cell:
    """Find the first step of the shortest path from `start` to `goal`.

    Args:
        maze: Row-major wall-bitmask grid.
        start: Current (x, y) cell.
        goal: Target (x, y) cell.

    Returns:
        The neighboring cell to move to next, or `start` unchanged if
        already at `goal`, or if `goal`/`start` is unreachable.
    """
    if start == goal:
        return start

    distances = bfs_distances(maze, goal)
    if start not in distances:
        return start

    best_step = start
    best_distance = distances[start]
    for neighbor in neighbors(maze, start):
        distance = distances.get(neighbor)
        if distance is not None and distance < best_distance:
            best_distance = distance
            best_step = neighbor
    return best_step


def farthest_cell_from(
        maze: List[List[int]], start: Cell, avoid: Cell) -> Cell:
    """Find the cell reachable from `start` that is farthest from `avoid`.

    Used to pick a flee target for an edible ghost: search the area
    reachable from the ghost's own position, and prefer whichever cell is
    hardest for the player to reach.

    Args:
        maze: Row-major wall-bitmask grid.
        start: The (x, y) cell to search reachability from (the ghost).
        avoid: The (x, y) cell to maximize distance from (the player).

    Returns:
        The reachable cell with the greatest path distance from `avoid`.
        Falls back to `start` if nothing farther is reachable.
    """
    distances_from_avoid = bfs_distances(maze, avoid)
    reachable_from_start = bfs_distances(maze, start)

    best_cell = start
    best_distance = distances_from_avoid.get(start, -1)
    for cell in reachable_from_start:
        distance = distances_from_avoid.get(cell, -1)
        if distance > best_distance:
            best_distance = distance
            best_cell = cell
    return best_cell


def _in_bounds(maze: List[List[int]], cell: Cell) -> bool:
    """Return whether `cell` falls within the maze's bounds."""
    height = len(maze)
    width = len(maze[0]) if height else 0
    x, y = cell
    return 0 <= x < width and 0 <= y < height
