"""
ai/heuristic.py
===============
Heuristic evaluation function for non-terminal game states.

Used by Minimax and Alpha-Beta when the depth limit is reached and the state
is not yet terminal. A good heuristic is fast to compute and correlates with
the probability of the evaluated player winning.

Heuristic Design (explainable for academic defense):
----------------------------------------------------
Primary term:
    score = my_points - opponent_points

    Intuition: The player with more remaining points wins. At any non-terminal
    state, a positive score means we are ahead; negative means behind.
    This alone is a perfectly valid and defensible first-order heuristic.

Secondary term (look-ahead bias):
    If it is my turn next AND the sequence is non-empty, we subtract a small
    fraction of max(left_end, right_end) from the score.

    Intuition: Whichever number I must take on my next turn will cost me points.
    If large numbers (2 or 3) are at the ends, I will likely lose more points
    shortly, so the position is slightly worse for me than the raw score difference
    suggests. The coefficient 0.1 keeps this term minor (max effect = 0.3)
    so it does not overwhelm the primary term.

    This term is optional; it can be disabled by setting ENABLE_LOOKAHEAD_BIAS=False.

Terminal evaluation (used directly, not via heuristic):
    If the game is over: +∞ for win, –∞ for loss, 0 for draw.
    (Handled in minimax/alphabeta, not here.)
"""

from game.state import GameState

# ── Configuration ──────────────────────────────────────────────────────────────
ENABLE_LOOKAHEAD_BIAS: bool = True   # Toggle the secondary look-ahead term
LOOKAHEAD_COEFF: float = 0.1         # Weight of the look-ahead penalty

# Large sentinel values for terminal states (set by search, not heuristic)
WIN_SCORE:  float = 1_000_000.0
LOSS_SCORE: float = -1_000_000.0
DRAW_SCORE: float = 0.0


def evaluate(state: GameState, player_id: int) -> float:
    """
    Heuristic evaluation of a non-terminal GameState from the perspective
    of *player_id*.

    Parameters
    ----------
    state : GameState
        The state to evaluate. Should NOT be terminal (call get_winner
        for terminal states instead).
    player_id : int
        The AI player for whom we are evaluating (1 or 2).

    Returns
    -------
    float
        Positive = good for player_id, Negative = bad for player_id.
    """
    # ── Primary term: point difference ────────────────────────────────────────
    my_pts  = state.p1_points if player_id == 1 else state.p2_points
    opp_pts = state.p2_points if player_id == 1 else state.p1_points
    score = float(my_pts - opp_pts)

    # ── Secondary term: look-ahead end-value bias ──────────────────────────────
    if ENABLE_LOOKAHEAD_BIAS and len(state.sequence) > 0:
        # Only penalise if it is OUR turn next (we will be forced to take an end)
        if state.turn == player_id:
            worst_end = max(state.sequence[0], state.sequence[-1])
            score -= LOOKAHEAD_COEFF * worst_end

    return score


def terminal_score(winner: int, player_id: int) -> float:
    """
    Return the exact score for a terminal state.

    Parameters
    ----------
    winner : int
        0 = draw, 1 = P1 wins, 2 = P2 wins  (from get_winner()).
    player_id : int
        The AI player for whom we are evaluating.

    Returns
    -------
    float
        WIN_SCORE, LOSS_SCORE, or DRAW_SCORE.
    """
    if winner == 0:
        return DRAW_SCORE
    return WIN_SCORE if winner == player_id else LOSS_SCORE
