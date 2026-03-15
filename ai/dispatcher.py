from __future__ import annotations

from typing import TYPE_CHECKING

from ai.alphabeta import get_best_move_alphabeta
from ai.minimax import get_best_move_minimax
from game.state import GameState

if TYPE_CHECKING:
    from experiments.runner import PlayerConfig


def get_best_ai_move(state: GameState, cfg: "PlayerConfig"):
    if cfg.kind == "minimax":
        move, _, stats = get_best_move_minimax(state, cfg.depth, state.turn)
    elif cfg.kind == "alphabeta":
        move, _, stats = get_best_move_alphabeta(state, cfg.depth, state.turn)
    else:
        raise ValueError(f"Unknown AI kind: {cfg.kind!r}")
    return move, stats
