from __future__ import annotations

import math
from typing import Tuple, Optional

from ai.heuristic import evaluate, terminal_score
from game.node import GameTreeNode
from game.rules import is_terminal, get_winner
from game.state import GameState


def search_value(
    node: GameTreeNode,
    depth: int,
    maximizing: bool,
    player_id: int,
    stats: "MoveStats",
    alpha: float,
    beta: float,
    use_pruning: bool,
) -> float:

    state = node.state

    if is_terminal(state):
        stats.nodes_evaluated += 1
        value = terminal_score(get_winner(state), player_id)
        node.value = value
        return value

    if depth == 0:
        stats.nodes_evaluated += 1
        value = evaluate(state, player_id)
        node.value = value
        return value

    node.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(node.children)

    if maximizing:
        value = -math.inf
        for child in node.children:
            child_value = search_value(
                child,
                depth - 1,
                False,
                player_id,
                stats,
                alpha,
                beta,
                use_pruning,
            )
            value = max(value, child_value)
            if use_pruning:
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
    else:
        value = math.inf
        for child in node.children:
            child_value = search_value(
                child,
                depth - 1,
                True,
                player_id,
                stats,
                alpha,
                beta,
                use_pruning,
            )
            value = min(value, child_value)
            if use_pruning:
                beta = min(beta, value)
                if beta <= alpha:
                    break

    node.value = value
    return value


def get_best_move(
    state: GameState,
    depth: int,
    player_id: int,
    stats: "MoveStats",
    use_pruning: bool,
) -> Tuple[str, float]:
    assert depth >= 1, "Search depth must be at least 1."
    assert state.turn == player_id, "Search called when it is not player_id's turn."
    assert not is_terminal(state), "Cannot search from a terminal state."

    root = GameTreeNode(state=state, move=None, parent=None, depth=0)
    root.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(root.children)

    best_move: Optional[str] = None
    best_value = -math.inf
    alpha = -math.inf
    beta = math.inf

    for child in root.children:
        child_value = search_value(
            child,
            depth - 1,
            False,
            player_id,
            stats,
            alpha,
            beta,
            use_pruning,
        )
        if child_value > best_value:
            best_value = child_value
            best_move = child.move
        if use_pruning:
            alpha = max(alpha, best_value)

    root.value = best_value
    assert best_move is not None, "Search returned no move (empty move list?)."
    return best_move, best_value
