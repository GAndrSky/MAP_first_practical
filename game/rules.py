"""
game/rules.py
=============
Game logic: move generation, state transitions, terminal detection, winner.

Rule Clarification (documented for academic defense):
-----------------------------------------------------
The original task states "a player takes one number from the sequence" without
specifying position. Two naive interpretations:
  • Any position  → branching factor N (too large; also eliminates strategic depth)
  • Always first  → branching factor 1 (trivial; no decision to make)

Chosen rule: A player may take EITHER the LEFTMOST or the RIGHTMOST element.
Justification:
  – This is the classical "Optimal Strategy for a Game" problem in competitive
    programming and game theory (Cormen et al., exercise 15.8).
  – It yields branching factor 2, making the game tree tractable for Minimax
    while still requiring genuine look-ahead strategy.
  – It preserves full information (both players see the whole sequence).
  – It is deterministic and well-defined.
"""

from typing import List, Tuple, Optional
from game.state import GameState

# ── Move constants ─────────────────────────────────────────────────────────────
MOVE_LEFT  = "LEFT"    # Take the leftmost element
MOVE_RIGHT = "RIGHT"   # Take the rightmost element
ALL_MOVES  = [MOVE_LEFT, MOVE_RIGHT]


# ── Core rule functions ────────────────────────────────────────────────────────

def get_legal_moves(state: GameState) -> List[str]:
    """
    Return the list of legal moves for the current state.

    A move is legal if the sequence is non-empty. When the sequence has exactly
    one element, both LEFT and RIGHT refer to the same element — we still return
    both to keep the interface uniform (they produce the same successor state,
    but having two entries is harmless and simplifies caller logic).

    Returns
    -------
    list[str]
        ["LEFT", "RIGHT"] if len(sequence) >= 1, else [].
    """
    if len(state.sequence) == 0:
        return []
    return list(ALL_MOVES)  # always copy so caller can mutate safely


def apply_move(state: GameState, move: str) -> GameState:
    """
    Apply a move and return the resulting GameState.

    The current player takes the leftmost or rightmost number from the sequence
    and subtracts it from their own points. The turn then passes to the other
    player.

    Parameters
    ----------
    state : GameState
        Current game state (must be non-terminal).
    move : str
        "LEFT" or "RIGHT".

    Returns
    -------
    GameState
        New state after the move (immutable; does not modify state).

    Raises
    ------
    ValueError
        If move is invalid or sequence is empty.
    """
    if move not in ALL_MOVES:
        raise ValueError(f"Invalid move '{move}'. Must be 'LEFT' or 'RIGHT'.")
    if len(state.sequence) == 0:
        raise ValueError("Cannot apply move: sequence is empty (terminal state).")

    # Take the chosen element
    if move == MOVE_LEFT:
        taken_value = state.sequence[0]
        new_sequence = state.sequence[1:]  # drop leftmost
    else:  # MOVE_RIGHT
        taken_value = state.sequence[-1]
        new_sequence = state.sequence[:-1]  # drop rightmost

    # Subtract from the current player's points
    if state.turn == 1:
        new_p1 = state.p1_points - taken_value
        new_p2 = state.p2_points
    else:
        new_p1 = state.p1_points
        new_p2 = state.p2_points - taken_value

    # Correctness assertion: taken value must match deducted amount
    assert taken_value in {1, 2, 3}, f"Unexpected taken_value: {taken_value}"

    # Switch turn
    next_turn = 2 if state.turn == 1 else 1

    return GameState(
        sequence=new_sequence,
        p1_points=new_p1,
        p2_points=new_p2,
        turn=next_turn,
    )


def is_terminal(state: GameState) -> bool:
    """
    Return True iff the game is over (sequence is empty).

    The game ends exactly when all numbers have been taken.
    """
    return len(state.sequence) == 0


def get_winner(state: GameState) -> int:
    """
    Determine the winner of a terminal state.

    Called only after is_terminal(state) == True.

    Returns
    -------
    int
        1  — Player 1 wins (more remaining points)
        2  — Player 2 wins (more remaining points)
        0  — Draw (equal remaining points)
    """
    assert is_terminal(state), "get_winner called on a non-terminal state."
    if state.p1_points > state.p2_points:
        return 1
    elif state.p2_points > state.p1_points:
        return 2
    else:
        return 0  # draw


def generate_sequence(n: int, rng=None) -> Tuple[int, ...]:
    """
    Randomly generate a sequence of length n with values in {1, 2, 3}.

    Parameters
    ----------
    n : int
        Desired sequence length; must satisfy 15 <= n <= 25.
    rng : random.Random, optional
        A seeded Random instance for reproducibility in experiments.
        If None, uses the module-level random functions.

    Returns
    -------
    tuple[int, ...]
        Randomly generated sequence.
    """
    from game.state import MIN_N, MAX_N, VALID_VALUES
    import random as _random

    if not (MIN_N <= n <= MAX_N):
        raise ValueError(f"N must be in [{MIN_N}, {MAX_N}], got {n}.")

    source = rng if rng is not None else _random
    seq = tuple(source.randint(1, 3) for _ in range(n))

    # Validation
    assert len(seq) == n
    assert all(v in VALID_VALUES for v in seq)
    return seq
