"""
ai/alphabeta.py
===============
Depth-limited Alpha-Beta Pruning — an optimized version of Minimax.

Algorithm overview (for academic defense):
------------------------------------------
Alpha-Beta pruning eliminates branches of the search tree that cannot possibly
affect the final decision. It maintains two bounds:
  • alpha — the best (highest) value that the MAXIMIZER can guarantee so far
  • beta  — the best (lowest)  value that the MINIMIZER can guarantee so far

Pruning conditions:
  • beta <= alpha in a maximizing node  →  the minimizer won't allow this branch
    (β-cutoff: prune remaining children)
  • beta <= alpha in a minimizing node  →  same reasoning from minimizer's side
    (α-cutoff)

Key property:
    Alpha-Beta produces the SAME result as Minimax for the same depth limit.
    It is purely an efficiency optimisation. In the best case (perfect move
    ordering), it reduces effective branching from b to √b, doubling the
    searchable depth for the same compute budget.

Complexity:
    Worst case: O(b^d)  (no pruning — same as Minimax)
    Best  case: O(b^(d/2))  (perfect move ordering)
    Average:    O(b^(3d/4))

Correctness note:
    Same maximizing-role convention as Minimax:
    maximizing = (state.turn == player_id)
"""

from __future__ import annotations
import math
from typing import Tuple, Optional

from game.node import GameTreeNode
from game.rules import is_terminal, get_winner
from game.state import GameState
from ai.heuristic import evaluate, terminal_score


# ── Transposition table (cache) ───────────────────────────────────────────────
CACHE = {}


def alphabeta(
    node: GameTreeNode,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    player_id: int,
    stats: "MoveStats",
) -> float:
    """
    Depth-limited Alpha-Beta Pruning search.

    Parameters
    ----------
    node : GameTreeNode
        Current node in the search tree.
    depth : int
        Remaining depth to search. 0 → evaluate with heuristic.
    alpha : float
        Best value the maximizer can guarantee (current path). Start: -∞
    beta : float
        Best value the minimizer can guarantee (current path). Start: +∞
    maximizing : bool
        True if the current player at this level is the maximizer.
    player_id : int
        The AI player being optimised (constant throughout search).
    stats : MoveStats
        Mutable statistics object; updated in-place.

    Returns
    -------
    float
        The backed-up Alpha-Beta value for this node.
    """
    state = node.state

    # ── Cache lookup ──────────────────────────────────────────────────────────
    key = (state, depth, maximizing)
    if key in CACHE:
        stats.nodes_evaluated += 1
        return CACHE[key]

    # ── Base cases ─────────────────────────────────────────────────────────────
    if is_terminal(state):
        stats.nodes_evaluated += 1
        winner = get_winner(state)
        value = terminal_score(winner, player_id)
        node.value = value
        CACHE[key] = value
        return value

    if depth == 0:
        stats.nodes_evaluated += 1
        value = evaluate(state, player_id)
        node.value = value
        CACHE[key] = value
        return value

    # ── Recursive step ─────────────────────────────────────────────────────────
    node.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(node.children)

    if maximizing:
        value = -math.inf
        for child in node.children:
            child_value = alphabeta(
                child,
                depth - 1,
                alpha,
                beta,
                False,          # opponent's turn → minimizing
                player_id,
                stats,
            )
            value = max(value, child_value)
            alpha = max(alpha, value)
            if beta <= alpha:
                # β-cutoff: the minimizer won't allow us to reach this branch
                break
        node.value = value
        CACHE[key] = value
        return value
    else:
        value = math.inf
        for child in node.children:
            child_value = alphabeta(
                child,
                depth - 1,
                alpha,
                beta,
                True,           # our turn → maximizing
                player_id,
                stats,
            )
            value = min(value, child_value)
            beta = min(beta, value)
            if beta <= alpha:
                # α-cutoff: the maximizer already has a better option elsewhere
                break
        node.value = value
        CACHE[key] = value
        return value


def get_best_move_alphabeta(
    state: GameState,
    depth: int,
    player_id: int,
) -> Tuple[str, float, "MoveStats"]:
    """
    Entry point: run Alpha-Beta from the given state and return the best move.

    Parameters
    ----------
    state : GameState
        Current game state (must be the AI player's turn).
    depth : int
        Search depth limit (≥ 1).
    player_id : int
        Which player the AI is (1 or 2).

    Returns
    -------
    (move, value, stats)
        move  : "LEFT" or "RIGHT"
        value : the backed-up value of the chosen move
        stats : MoveStats with accumulated node counts
    """
    from experiments.runner import MoveStats

    assert depth >= 1, "Search depth must be at least 1."
    assert state.turn == player_id, (
        "get_best_move_alphabeta called but it is not player_id's turn."
    )
    from game.rules import is_terminal as _is_terminal
    assert not _is_terminal(state), "Cannot search from a terminal state."

    root = GameTreeNode(state=state, move=None, parent=None, depth=0)
    stats = MoveStats()

    root.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(root.children)

    best_move: Optional[str] = None
    best_value = -math.inf
    alpha = -math.inf
    beta  = math.inf

    for child in root.children:
        child_value = alphabeta(
            child,
            depth - 1,
            alpha,
            beta,
            False,               # After our move, opponent minimises
            player_id,
            stats,
        )
        if child_value > best_value:
            best_value = child_value
            best_move = child.move
        alpha = max(alpha, best_value)

    root.value = best_value
    assert best_move is not None, "Alpha-Beta returned no move (empty move list?)."
    return best_move, best_value, stats