from ai.minimax import get_best_move_minimax
from ai.alphabeta import get_best_move_alphabeta


def get_best_ai_move(state, cfg):
    if cfg.kind == "minimax":
        move, _, stats = get_best_move_minimax(state, cfg.depth, state.turn)
    elif cfg.kind == "alphabeta":
        move, _, stats = get_best_move_alphabeta(state, cfg.depth, state.turn)
    else:
        raise ValueError(f"Unknown AI kind: {cfg.kind!r}")
    return move, stats