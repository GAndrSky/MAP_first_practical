from __future__ import annotations

import math
from typing import Tuple

from game.node import GameTreeNode
from game.state import GameState

from ai.search_core import search_value, get_best_move


def alphabeta(
    node: GameTreeNode,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    player_id: int,
    stats: "MoveStats",
) -> float:
    return search_value(
        node=node,
        depth=depth,
        maximizing=maximizing,
        player_id=player_id,
        stats=stats,
        alpha=alpha,
        beta=beta,
        use_pruning=True,
    )


def get_best_move_alphabeta(
    state: GameState,
    depth: int,
    player_id: int,
) -> Tuple[str, float, "MoveStats"]:
    from experiments.runner import MoveStats

    stats = MoveStats()
    best_move, best_value = get_best_move(
        state=state,
        depth=depth,
        player_id=player_id,
        stats=stats,
        use_pruning=True,
    )
    return best_move, best_value, stats
