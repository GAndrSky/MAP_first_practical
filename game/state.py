from dataclasses import dataclass
from typing import Tuple

INITIAL_POINTS: int = 80
MIN_N: int = 15
MAX_N: int = 25
VALID_VALUES = frozenset({1, 2, 3})


@dataclass(frozen=True)
class GameState:
    sequence: Tuple[int, ...]
    p1_points: int
    p2_points: int
    turn: int

    def __post_init__(self) -> None:
        assert self.turn in (1, 2), f"turn must be 1 or 2, got {self.turn}"
        assert self.p1_points >= 0, "p1_points cannot be negative"
        assert self.p2_points >= 0, "p2_points cannot be negative"
        assert all(v in VALID_VALUES for v in self.sequence), (
            f"Sequence contains value outside {{1,2,3}}: {self.sequence}"
        )

    def __repr__(self) -> str:
        return (
            f"GameState(seq={list(self.sequence)}, "
            f"P1={self.p1_points}, P2={self.p2_points}, turn={self.turn})"
        )


def make_initial_state(sequence: Tuple[int, ...], first_player: int = 1) -> GameState:
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
