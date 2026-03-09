"""
ai/minimax.py
=============
Thin Minimax wrapper over shared search core.
"""

from __future__ import annotations

import math
from typing import Tuple

from game.node import GameTreeNode
from game.state import GameState

from ai.search_core import search_value, get_best_move


def minimax(
    node: GameTreeNode,
    depth: int,
    maximizing: bool,
    player_id: int,
    stats: "MoveStats",
) -> float:
    """Depth-limited Minimax value for a node."""
    return search_value(
        node=node,
        depth=depth,
        maximizing=maximizing,
        player_id=player_id,
        stats=stats,
        alpha=-math.inf,
        beta=math.inf,
        use_pruning=False,
    )


def get_best_move_minimax(
    state: GameState,
    depth: int,
    player_id: int,
) -> Tuple[str, float, "MoveStats"]:
    """Return (best_move, value, stats) using plain Minimax."""
    from experiments.runner import MoveStats

    stats = MoveStats()
    best_move, best_value = get_best_move(
        state=state,
        depth=depth,
        player_id=player_id,
        stats=stats,
        use_pruning=False,
    )
    return best_move, best_value, stats
