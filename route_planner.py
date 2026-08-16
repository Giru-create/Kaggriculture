"""
Route Planner for Kaggle Kaggriculture Competition
Provides pathfinding and task assignment utilities.
"""

from typing import Dict, List, Optional, Tuple, Union


# Position type: either a tuple or list of (x, y)
Position = Union[Tuple[int, int], List[int]]


def get_shed_coordinates(board_size: int = 10) -> List[Tuple[int, int]]:
    """
    Get the 4 tiles orthogonally adjacent to the shed.

    The shed is located at the center of the board. These adjacent tiles
    are where you can PICKUP/DROP items from the shed.

    Args:
        board_size: The size of the game board (default 10).

    Returns:
        List of (x, y) tuples for tiles adjacent to the shed.

    Examples:
        >>> get_shed_coordinates(10)
        [(4, 4), (5, 4), (4, 5), (5, 5)]
    """
    # Shed is at the center of the board (coordinates 4-5 on a 10x10 board)
    center = board_size // 2
    return [
        (center - 1, center - 1),  # Top-left of shed
        (center, center - 1),      # Top-right of shed
        (center - 1, center),      # Bottom-left of shed
        (center, center),          # Bottom-right of shed
    ]


def manhattan_distance(pos1: Position, pos2: Position) -> int:
    """
    Calculate the Manhattan distance between two positions.

    Manhattan distance is the sum of absolute differences in x and y
    coordinates: |x1-x2| + |y1-y2|.

    Args:
        pos1: First position as [x, y] or (x, y).
        pos2: Second position as [x, y] or (x, y).

    Returns:
        The Manhattan distance (integer).

    Examples:
        >>> manhattan_distance((0, 0), (3, 4))
        7
        >>> manhattan_distance([1, 2], [4, 6])
        7
        >>> manhattan_distance((5, 5), (5, 5))
        0
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def find_nearest_target(
    farmer_pos: Position,
    targets: List[Position],
    tiles_grid: Optional[List[List]] = None,
) -> Optional[Tuple[int, int]]:
    """
    Find the nearest target position to the farmer.

    Uses Manhattan distance to find the closest target. If multiple targets
    are equally near, returns the first one found.

    Args:
        farmer_pos: The farmer's current position as [x, y] or (x, y).
        targets: List of target positions as [(x, y), ...].
        tiles_grid: Optional grid of tiles (reserved for future pathfinding).

    Returns:
        The (x, y) tuple of the nearest target, or None if no targets.

    Examples:
        >>> find_nearest_target((0, 0), [(3, 4), (1, 1), (2, 2)])
        (1, 1)
        >>> find_nearest_target((5, 5), [])
        None
    """
    if not targets:
        return None

    nearest = None
    min_distance = float("inf")

    for target in targets:
        dist = manhattan_distance(farmer_pos, target)
        if dist < min_distance:
            min_distance = dist
            nearest = (target[0], target[1])

    return nearest


def generate_movement_actions(
    start_pos: Position, target_pos: Position
) -> List[str]:
    """
    Generate movement actions to travel from start to target.

    Uses simple Manhattan pathing: moves horizontally first (EAST/WEST),
    then vertically (NORTH/SOUTH). This provides a direct path without
    obstacles.

    Args:
        start_pos: Starting position as [x, y] or (x, y).
        target_pos: Target position as [x, y] or (x, y).

    Returns:
        List of movement actions: ["NORTH", "SOUTH", "EAST", "WEST"].

    Examples:
        >>> generate_movement_actions((4, 4), (6, 5))
        ['EAST', 'EAST', 'SOUTH']
        >>> generate_movement_actions((5, 5), (3, 2))
        ['WEST', 'WEST', 'NORTH', 'NORTH']
        >>> generate_movement_actions((4, 4), (4, 4))
        []
    """
    if start_pos[0] == target_pos[0] and start_pos[1] == target_pos[1]:
        return []

    actions = []

    # Move horizontally first
    dx = target_pos[0] - start_pos[0]
    if dx > 0:
        actions.extend(["EAST"] * dx)
    elif dx < 0:
        actions.extend(["WEST"] * abs(dx))

    # Then move vertically
    dy = target_pos[1] - start_pos[1]
    if dy > 0:
        actions.extend(["SOUTH"] * dy)
    elif dy < 0:
        actions.extend(["NORTH"] * abs(dy))

    return actions


def assign_tasks_to_hands(
    hands_positions: List[Position],
    tasks: List[Position],
    farmer_pos: Optional[Position] = None,
) -> Dict[int, List[Tuple[int, int]]]:
    """
    Assign tasks to hands using greedy nearest-neighbor assignment.

    Each task is assigned to the nearest available hand. Once a hand is
    assigned a task, it remains available for additional tasks.

    Args:
        hands_positions: List of hand positions as [[x, y], ...].
        tasks: List of task positions as [(x, y), ...].
        farmer_pos: Optional farmer position (reserved for future use).

    Returns:
        Dictionary mapping hand_index -> list of (x, y) tasks assigned.

    Examples:
        >>> hands = [(0, 0), (9, 9)]
        >>> tasks = [(1, 1), (8, 8)]
        >>> assign_tasks_to_hands(hands, tasks)
        {0: [(1, 1)], 1: [(8, 8)]}
        >>> assign_tasks_to_hands([], [(1, 1)])
        {}
        >>> assign_tasks_to_hands([(0, 0)], [])
        {0: []}
    """
    # Initialize result with empty lists for each hand
    assignments: Dict[int, List[Tuple[int, int]]] = {
        i: [] for i in range(len(hands_positions))
    }

    if not hands_positions or not tasks:
        return assignments

    # Greedy assignment: for each task, find nearest hand
    for task in tasks:
        best_hand = None
        best_distance = float("inf")

        for hand_idx, hand_pos in enumerate(hands_positions):
            dist = manhattan_distance(hand_pos, task)
            if dist < best_distance:
                best_distance = dist
                best_hand = hand_idx

        if best_hand is not None:
            assignments[best_hand].append((task[0], task[1]))

    return assignments
