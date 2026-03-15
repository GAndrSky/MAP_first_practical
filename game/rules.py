from typing import List, Tuple, Optional
from game.state import GameState

MOVE_LEFT  = "LEFT"   
MOVE_RIGHT = "RIGHT"   
ALL_MOVES  = [MOVE_LEFT, MOVE_RIGHT]

def get_legal_moves(state: GameState) -> List[str]:
    if len(state.sequence) == 0:
        return []
    return list(ALL_MOVES)


def apply_move(state: GameState, move: str) -> GameState:
    if move not in ALL_MOVES:
        raise ValueError(f"Invalid move '{move}'. Must be 'LEFT' or 'RIGHT'.")
    if len(state.sequence) == 0:
        raise ValueError("Cannot apply move: sequence is empty (terminal state).")

    if move == MOVE_LEFT:
        taken_value = state.sequence[0]
        new_sequence = state.sequence[1:]  
    else:  
        taken_value = state.sequence[-1]
        new_sequence = state.sequence[:-1] 

    if state.turn == 1:
        new_p1 = state.p1_points - taken_value
        new_p2 = state.p2_points
    else:
        new_p1 = state.p1_points
        new_p2 = state.p2_points - taken_value

    assert taken_value in {1, 2, 3}, f"Unexpected taken_value: {taken_value}"

    next_turn = 2 if state.turn == 1 else 1

    return GameState(
        sequence=new_sequence,
        p1_points=new_p1,
        p2_points=new_p2,
        turn=next_turn,
    )


def is_terminal(state: GameState) -> bool:
    return len(state.sequence) == 0


def get_winner(state: GameState) -> int:
    assert is_terminal(state), "get_winner called on a non-terminal state."
    if state.p1_points > state.p2_points:
        return 1
    elif state.p2_points > state.p1_points:
        return 2
    else:
        return 0  # draw


def generate_sequence(n: int, rng=None) -> Tuple[int, ...]:
    from game.state import MIN_N, MAX_N, VALID_VALUES
    import random as _random

    if not (MIN_N <= n <= MAX_N):
        raise ValueError(f"N must be in [{MIN_N}, {MAX_N}], got {n}.")

    source = rng if rng is not None else _random
    seq = tuple(source.randint(1, 3) for _ in range(n))

    assert len(seq) == n
    assert all(v in VALID_VALUES for v in seq)
    return seq
