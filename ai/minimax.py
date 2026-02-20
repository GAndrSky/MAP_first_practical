"""
ai/minimax.py
=============
Depth-limited Minimax algorithm with dynamic game tree generation.

Algorithm overview (for academic defense):
------------------------------------------
Minimax is a recursive adversarial search algorithm for two-player zero-sum
games with perfect information. It assumes:
  • The maximizing player picks the move with the HIGHEST value.
  • The minimizing player picks the move with the LOWEST value.
  • Both players play optimally.

Depth-limited variant:
    When the recursion reaches the depth limit and the state is not terminal,
    we call the heuristic evaluation function instead of continuing the search.
    This bounds the time/space complexity at the cost of evaluation accuracy.

Complexity:
    Time:  O(b^d)  where b = branching factor (2), d = depth limit
    Space: O(b*d)  for the call stack (tree nodes are not all kept in memory)

Correctness note — maximizing role:
    The maximizing flag is determined by whose turn it is vs. who we are
    optimising for. If it is our turn  → we maximise;
    if it is the opponent's turn → we minimise.
    This is passed in as the initial `maximizing` argument and flipped at
    each level as the turn alternates.
"""

from __future__ import annotations
import math
from typing import Tuple, Optional

from game.node import GameTreeNode
from game.rules import get_legal_moves, apply_move, is_terminal, get_winner
from game.state import GameState
from ai.heuristic import evaluate, terminal_score


def minimax(
    node: GameTreeNode,
    depth: int,
    maximizing: bool,
    player_id: int,
    stats: "MoveStats",
) -> float:
    """
    Depth-limited Minimax search.

    Parameters
    ----------
    node : GameTreeNode
        Current node in the search tree.
    depth : int
        Remaining depth to search. 0 → evaluate with heuristic.
    maximizing : bool
        True if the current level is the maximizing player's turn.
    player_id : int
        The AI player we are optimising for (1 or 2). Constant throughout
        the entire search from a given root call.
    stats : MoveStats
        Mutable statistics object; updated in-place.

    Returns
    -------
    float
        The backed-up Minimax value for this node.
    """
    state = node.state

    # ── Base cases ─────────────────────────────────────────────────────────────
    if is_terminal(state):
        stats.nodes_evaluated += 1
        winner = get_winner(state)
        value = terminal_score(winner, player_id)
        node.value = value
        return value

    if depth == 0:
        stats.nodes_evaluated += 1
        value = evaluate(state, player_id)
        node.value = value
        return value

    # ── Recursive step ─────────────────────────────────────────────────────────
    # Expand children if not already done
    node.expand(nodes_generated_counter=None)  # counter incremented manually below
    stats.nodes_generated += len(node.children)

    if maximizing:
        best_value = -math.inf
        for child in node.children:
            child_value = minimax(
                child,
                depth - 1,
                False,         # opponent's turn → minimizing
                player_id,
                stats,
            )
            if child_value > best_value:
                best_value = child_value
        node.value = best_value
        return best_value
    else:
        best_value = math.inf
        for child in node.children:
            child_value = minimax(
                child,
                depth - 1,
                True,          # our turn again → maximizing
                player_id,
                stats,
            )
            if child_value < best_value:
                best_value = child_value
        node.value = best_value
        return best_value


def get_best_move_minimax(
    state: GameState,
    depth: int,
    player_id: int,
) -> Tuple[str, float, "MoveStats"]:
    """
    Entry point: run Minimax from the given state and return the best move.

    The maximizing flag at the root is True iff it is the AI's turn.
    (state.turn == player_id  →  AI is moving now  →  maximising)

    Parameters
    ----------
    state : GameState
        Current game state (the AI's turn must match player_id for the
        maximizing flag to be set correctly).
    depth : int
        Search depth limit (≥ 1).
    player_id : int
        Which player the AI is (1 or 2).

    Returns
    -------
    (move, value, stats)
        move  : "LEFT" or "RIGHT"
        value : the Minimax value of the chosen move
        stats : MoveStats with node counts
    """
    # Import here to avoid circular imports at module level
    from experiments.runner import MoveStats

    assert depth >= 1, "Search depth must be at least 1."
    assert state.turn == player_id, (
        "get_best_move_minimax called but it is not player_id's turn."
    )
    assert not is_terminal(state), "Cannot search from a terminal state."

    root = GameTreeNode(state=state, move=None, parent=None, depth=0)
    stats = MoveStats()

    # Root is always maximizing (it IS the AI's turn)
    maximizing_at_root = True  # state.turn == player_id, checked above

    root.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(root.children)

    best_move: Optional[str] = None
    best_value = -math.inf

    for child in root.children:
        child_value = minimax(
            child,
            depth - 1,
            False,               # After our move, opponent minimises
            player_id,
            stats,
        )
        if child_value > best_value:
            best_value = child_value
            best_move = child.move

    root.value = best_value
    assert best_move is not None, "Minimax returned no move (empty move list?)."
    return best_move, best_value, stats
