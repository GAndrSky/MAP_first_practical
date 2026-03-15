from __future__ import annotations
import math
from typing import Tuple, Optional

from game.node import GameTreeNode
from game.rules import get_legal_moves, apply_move, is_terminal, get_winner
from game.state import GameState
from ai.heuristic import evaluate, terminal_score

CACHE = {}

def minimax(
    node: GameTreeNode,
    depth: int,
    maximizing: bool,
    player_id: int,
    stats: "MoveStats",
) -> float:
    
    state = node.state

    key = (state, depth, maximizing)
    if key in CACHE:
        stats.nodes_evaluated += 1
        return CACHE[key]

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

    node.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(node.children)

    if maximizing:
        best_value = -math.inf
        for child in node.children:
            child_value = minimax(
                child,
                depth - 1,
                False,        
                player_id,
                stats,
            )
            if child_value > best_value:
                best_value = child_value
        node.value = best_value
        CACHE[key] = best_value
        return best_value
    else:
        best_value = math.inf
        for child in node.children:
            child_value = minimax(
                child,
                depth - 1,
                True,         
                player_id,
                stats,
            )
            if child_value < best_value:
                best_value = child_value
        node.value = best_value
        CACHE[key] = best_value
        return best_value

def get_best_move_minimax(
    state: GameState,
    depth: int,
    player_id: int,
) -> Tuple[str, float, "MoveStats"]:
    
    from experiments.runner import MoveStats

    assert depth >= 1, "Search depth must be at least 1."
    assert state.turn == player_id, (
        "get_best_move_minimax called but it is not player_id's turn."
    )
    assert not is_terminal(state), "Cannot search from a terminal state."

    root = GameTreeNode(state=state, move=None, parent=None, depth=0)
    stats = MoveStats()

    maximizing_at_root = True  

    root.expand(nodes_generated_counter=None)
    stats.nodes_generated += len(root.children)

    best_move: Optional[str] = None
    best_value = -math.inf

    for child in root.children:
        child_value = minimax(
            child,
            depth - 1,
            False, 
            player_id,
            stats,
        )
        if child_value > best_value:
            best_value = child_value
            best_move = child.move

    root.value = best_value
    assert best_move is not None, "Minimax returned no move (empty move list?)."
    return best_move, best_value, stats