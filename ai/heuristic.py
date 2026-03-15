from game.state import GameState

ENABLE_LOOKAHEAD_BIAS: bool = True  
LOOKAHEAD_COEFF: float = 0.1         

WIN_SCORE:  float = 1_000_000.0
LOSS_SCORE: float = -1_000_000.0
DRAW_SCORE: float = 0.0

def evaluate(state: GameState, player_id: int) -> float:
    my_pts  = state.p1_points if player_id == 1 else state.p2_points
    opp_pts = state.p2_points if player_id == 1 else state.p1_points
    score = float(my_pts - opp_pts)

    if ENABLE_LOOKAHEAD_BIAS and len(state.sequence) > 0:
        if state.turn == player_id:
            worst_end = max(state.sequence[0], state.sequence[-1])
            score -= LOOKAHEAD_COEFF * worst_end

    return score

def terminal_score(winner: int, player_id: int) -> float:
    if winner == 0:
        return DRAW_SCORE
    return WIN_SCORE if winner == player_id else LOSS_SCORE
