"""
game/state.py
=============
Defines the GameState dataclass — the fundamental unit of the game tree.

A GameState is IMMUTABLE (uses tuple for sequence) so that child states
can be safely created without aliasing the parent's data. This is critical
for correct tree generation in Minimax / Alpha-Beta.

Academic note:
    turn ∈ {1, 2}  — player 1 moves first by convention.
    p1_points, p2_points start at INITIAL_POINTS and decrease as numbers
    are taken. The player with MORE points at game end wins.
"""

from dataclasses import dataclass, field
from typing import Tuple

# ── Constants ─────────────────────────────────────────────────────────────────
INITIAL_POINTS: int = 80        # Each player begins with 80 points
MIN_N: int = 15                 # Minimum sequence length
MAX_N: int = 25                 # Maximum sequence length
VALID_VALUES = frozenset({1, 2, 3})  # Allowed numbers in the sequence


@dataclass(frozen=True)
class GameState:
    """
    Immutable snapshot of the game at a single moment.

    Attributes
    ----------
    sequence : tuple[int, ...]
        The remaining numbers in the sequence. Leftmost = index 0.
    p1_points : int
        Remaining points for Player 1.
    p2_points : int
        Remaining points for Player 2.
    turn : int
        Whose turn it is: 1 for Player 1, 2 for Player 2.
    """
    sequence: Tuple[int, ...]
    p1_points: int
    p2_points: int
    turn: int

    # ── Validation ────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        """Validate state invariants (can be stripped for production)."""
        assert self.turn in (1, 2), f"turn must be 1 or 2, got {self.turn}"
        assert self.p1_points >= 0, "p1_points cannot be negative"
        assert self.p2_points >= 0, "p2_points cannot be negative"
        assert all(v in VALID_VALUES for v in self.sequence), (
            f"Sequence contains value outside {{1,2,3}}: {self.sequence}"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    # @property
    # def current_player_points(self) -> int:
    #     """Points of the player whose turn it currently is."""
    #     return self.p1_points if self.turn == 1 else self.p2_points

    # @property
    # def opponent_points(self) -> int:
    #     """Points of the player who is NOT currently moving."""
    #     return self.p2_points if self.turn == 1 else self.p1_points

    # def points_of(self, player_id: int) -> int:
    #     """Return points for the given player (1 or 2)."""
    #     return self.p1_points if player_id == 1 else self.p2_points

    def __repr__(self) -> str:
        return (
            f"GameState(seq={list(self.sequence)}, "
            f"P1={self.p1_points}, P2={self.p2_points}, turn={self.turn})"
        )


def make_initial_state(sequence: Tuple[int, ...], first_player: int = 1) -> GameState:
    """
    Create the root GameState for a new game.

    Parameters
    ----------
    sequence : tuple[int, ...]
        The randomly generated sequence (length N, values in {1,2,3}).
    first_player : int
        Which player moves first (1 or 2).

    Returns
    -------
    GameState
        The initial state of the game.
    """
    assert MIN_N <= len(sequence) <= MAX_N, (
        f"Sequence length must be [{MIN_N}, {MAX_N}], got {len(sequence)}"
    )
    assert first_player in (1, 2), "first_player must be 1 or 2"
    return GameState(
        sequence=tuple(sequence),
        p1_points=INITIAL_POINTS,
        p2_points=INITIAL_POINTS,
        turn=first_player,
    )
