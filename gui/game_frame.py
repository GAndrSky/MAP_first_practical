"""
gui/game_frame.py
=================
Live game view: sequence display, scoreboard, move buttons, and status.

Handles both Human vs AI and AI vs AI modes.

Human moves: LEFT / RIGHT buttons (or click the first/last sequence tile).
AI moves: triggered automatically via after() so the GUI remains responsive.
"""

import tkinter as tk
from tkinter import messagebox
import time

from game.state import GameState, make_initial_state
from game.rules import apply_move, is_terminal, get_winner, MOVE_LEFT, MOVE_RIGHT
from ai.dispatcher import get_best_ai_move
from experiments.runner import MoveStats, MoveRecord, GameRecord, PlayerConfig


# ── Colour palette (Catppuccin Mocha) ─────────────────────────────────────────
BG       = "#1e1e2e"
SURFACE  = "#313244"
OVERLAY  = "#45475a"
BLUE     = "#89b4fa"
GREEN    = "#a6e3a1"
RED      = "#f38ba8"
YELLOW   = "#f9e2af"
TEXT     = "#cdd6f4"
SUBTEXT  = "#a6adc8"
TEAL     = "#94e2d5"


class GameFrame(tk.Frame):
    """
    Main game screen displayed while a game is in progress.

    Parameters
    ----------
    parent : tk.Widget
    on_back : callable
        Called when the user clicks "Back to Setup".
    """

    def __init__(self, parent, on_back, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._on_back = on_back
        self._state: GameState = None
        self._mode: str = None         # "human_vs_ai" | "ai_vs_ai"
        self._p1_config: PlayerConfig = None
        self._p2_config: PlayerConfig = None
        self._game_record: GameRecord = None
        self._move_index: int = 0
        self._game_over: bool = False
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header row ─────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(fill=tk.X, padx=20, pady=(16, 4))

        tk.Button(
            header, text="← Back", command=self._back,
            bg=OVERLAY, fg=TEXT, activebackground=SURFACE,
            font=("Segoe UI", 9), relief=tk.FLAT, padx=8, pady=3,
        ).pack(side=tk.LEFT)

        tk.Label(
            header, text="Number Sequence Game",
            font=("Segoe UI", 14, "bold"), fg=TEXT, bg=BG,
        ).pack(side=tk.LEFT, padx=16)

        # ── Scoreboard ─────────────────────────────────────────────────────────
        score_frame = tk.Frame(self, bg=SURFACE, pady=10)
        score_frame.pack(fill=tk.X, padx=20, pady=6)

        self._p1_label = tk.Label(
            score_frame, text="Player 1 (Human)\n80 pts",
            font=("Segoe UI", 11, "bold"), fg=BLUE, bg=SURFACE, padx=20,
        )
        self._p1_label.pack(side=tk.LEFT, expand=True)

        self._turn_label = tk.Label(
            score_frame, text="Turn: P1",
            font=("Segoe UI", 11, "bold"), fg=YELLOW, bg=SURFACE,
        )
        self._turn_label.pack(side=tk.LEFT, expand=True)

        self._p2_label = tk.Label(
            score_frame, text="Player 2 (AI)\n80 pts",
            font=("Segoe UI", 11, "bold"), fg=RED, bg=SURFACE, padx=20,
        )
        self._p2_label.pack(side=tk.LEFT, expand=True)

        # ── Status bar ─────────────────────────────────────────────────────────
        self._status_label = tk.Label(
            self, text="", font=("Segoe UI", 10, "italic"),
            fg=GREEN, bg=BG,
        )
        self._status_label.pack(pady=(4, 2))

        # ── Sequence display ────────────────────────────────────────────────────
        seq_outer = tk.Frame(self, bg=BG)
        seq_outer.pack(fill=tk.X, padx=20, pady=8)

        tk.Label(
            seq_outer, text="Sequence:", font=("Segoe UI", 10, "bold"),
            fg=SUBTEXT, bg=BG,
        ).pack(anchor=tk.W)

        self._seq_frame = tk.Frame(seq_outer, bg=BG)
        self._seq_frame.pack(fill=tk.X)

        # ── Move buttons (Human only) ───────────────────────────────────────────
        self._btn_frame = tk.Frame(self, bg=BG)
        self._btn_frame.pack(pady=12)

        self._left_btn = tk.Button(
            self._btn_frame, text="◀  Take LEFT",
            command=lambda: self._human_move(MOVE_LEFT),
            bg=BLUE, fg=BG, activebackground=TEAL,
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT,
            padx=18, pady=8, state=tk.DISABLED,
        )
        self._left_btn.pack(side=tk.LEFT, padx=12)

        self._right_btn = tk.Button(
            self._btn_frame, text="Take RIGHT  ▶",
            command=lambda: self._human_move(MOVE_RIGHT),
            bg=BLUE, fg=BG, activebackground=TEAL,
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT,
            padx=18, pady=8, state=tk.DISABLED,
        )
        self._right_btn.pack(side=tk.LEFT, padx=12)

        # ── Move history log ────────────────────────────────────────────────────
        log_outer = tk.Frame(self, bg=BG)
        log_outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(8, 4))

        tk.Label(
            log_outer, text="Move History:", font=("Segoe UI", 9, "bold"),
            fg=SUBTEXT, bg=BG,
        ).pack(anchor=tk.W)

        log_scroll = tk.Scrollbar(log_outer)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_text = tk.Text(
            log_outer, height=8, state=tk.DISABLED,
            bg=SURFACE, fg=TEXT, font=("Consolas", 9),
            yscrollcommand=log_scroll.set, relief=tk.FLAT,
            selectbackground=OVERLAY,
        )
        self._log_text.pack(fill=tk.BOTH, expand=True)
        log_scroll.config(command=self._log_text.yview)

    # ── Game lifecycle ─────────────────────────────────────────────────────────

    def start_game(self, config: dict):
        """
        Initialise and begin a new game from the given configuration dict.

        Expected keys: mode, sequence, first_player,
                       p1_kind, p1_depth, p2_kind, p2_depth
        """
        self._mode = config["mode"]
        self._game_over = False
        self._move_index = 0

        self._p1_config = PlayerConfig(
            player_id=1, kind=config["p1_kind"], depth=config["p1_depth"]
        )
        self._p2_config = PlayerConfig(
            player_id=2, kind=config["p2_kind"], depth=config["p2_depth"]
        )

        self._state = make_initial_state(
            config["sequence"], first_player=config["first_player"]
        )

        self._game_record = GameRecord(
            game_id=0,
            initial_sequence=config["sequence"],
            starting_player=config["first_player"],
            p1_config=self._p1_config,
            p2_config=self._p2_config,
        )

        # Update labels
        p1_name = "Human" if self._p1_config.kind == "human" else f"AI ({self._p1_config.kind})"
        p2_name = f"AI ({self._p2_config.kind}, d={self._p2_config.depth})"
        self._p1_label.config(text=f"Player 1  {p1_name}\n{self._state.p1_points} pts")
        self._p2_label.config(text=f"Player 2  {p2_name}\n{self._state.p2_points} pts")

        self._clear_log()
        self._refresh_ui()
        self._advance_game()

    def _advance_game(self):
        """Called after every state transition. Decides what happens next."""
        if is_terminal(self._state):
            self._finish_game()
            return

        current = self._state.turn
        cfg = self._p1_config if current == 1 else self._p2_config

        if cfg.kind == "human":
            self._set_status("Your turn — choose LEFT or RIGHT")
            self._set_buttons_enabled(True)
        else:
            self._set_buttons_enabled(False)
            self._set_status(f"AI ({cfg.kind}, depth={cfg.depth}) is thinking…")
            # Schedule AI move after a brief delay so the UI updates first
            self.after(80, self._ai_move)

    def _human_move(self, move: str):
        """Handle a human button click."""
        if self._game_over:
            return
        self._set_buttons_enabled(False)
        self._apply_and_record(move, algo="human", nodes_gen=0, nodes_eval=0, t=0.0)
        self._advance_game()

    def _ai_move(self):
        """Run the AI algorithm and apply its chosen move."""
        if self._game_over:
            return
        current = self._state.turn
        cfg = self._p1_config if current == 1 else self._p2_config

        t_start = time.perf_counter()
        move, stats = get_best_ai_move(self._state, cfg)
        elapsed = time.perf_counter() - t_start

        self._apply_and_record(
            move, algo=cfg.kind,
            nodes_gen=stats.nodes_generated,
            nodes_eval=stats.nodes_evaluated,
            t=elapsed,
        )
        self._advance_game()

    def _apply_and_record(self, move, algo, nodes_gen, nodes_eval, t):
        """Apply move, record it, and refresh the UI."""
        player = self._state.turn
        value_taken = self._state.sequence[0] if move == MOVE_LEFT else self._state.sequence[-1]

        new_state = apply_move(self._state, move)
        self._state = new_state

        mr = MoveRecord(
            move_index=self._move_index,
            player_turn=player,
            action=move,
            value_taken=value_taken,
            p1_points_after=new_state.p1_points,
            p2_points_after=new_state.p2_points,
            sequence_after=new_state.sequence,
            time_s=t,
            nodes_generated=nodes_gen,
            nodes_evaluated=nodes_eval,
            algorithm=algo,
        )
        self._game_record.moves.append(mr)
        self._move_index += 1

        # Log entry
        who = f"P{player}"
        stats_str = ""
        if algo != "human":
            stats_str = f" | gen={nodes_gen} eval={nodes_eval} {t*1000:.1f}ms"
        self._log(f"Move {self._move_index:>2}: {who} took {move} ({value_taken}) "
                  f"→ P1:{new_state.p1_points} P2:{new_state.p2_points}{stats_str}")

        self._refresh_ui()

    def _finish_game(self):
        """Game over — display result and finalise record."""
        self._game_over = True
        self._set_buttons_enabled(False)

        winner = get_winner(self._state)
        self._game_record.winner = winner
        self._game_record.final_p1_points = self._state.p1_points
        self._game_record.final_p2_points = self._state.p2_points

        if winner == 0:
            msg = "It's a DRAW! 🤝"
            colour = YELLOW
        elif winner == 1:
            msg = "Player 1 WINS! 🏆"
            colour = GREEN
        else:
            msg = "Player 2 WINS! 🏆"
            colour = RED

        result_str = (f"Final: P1={self._state.p1_points}  P2={self._state.p2_points}  "
                      f"→ {msg}")
        self._set_status(result_str)
        self._status_label.config(fg=colour)
        self._log(f"\n{'═'*50}\n{result_str}\n{'═'*50}")

    # ── UI helpers ─────────────────────────────────────────────────────────────

    def _refresh_ui(self):
        """Re-render the sequence tiles and update the scoreboard."""
        # Clear old tiles
        for w in self._seq_frame.winfo_children():
            w.destroy()

        seq = self._state.sequence
        for i, val in enumerate(seq):
            # Highlight the ends (left-most and right-most)
            if i == 0 or i == len(seq) - 1:
                bg_col = BLUE if val == 1 else (YELLOW if val == 2 else RED)
                border = 2
            else:
                bg_col = OVERLAY
                border = 0

            tile = tk.Label(
                self._seq_frame, text=str(val),
                font=("Segoe UI", 10, "bold"),
                bg=bg_col, fg=BG if (i == 0 or i == len(seq) - 1) else TEXT,
                width=2, pady=4, relief=tk.FLAT,
                highlightthickness=border, highlightbackground=TEXT,
            )
            tile.pack(side=tk.LEFT, padx=1, pady=2)

        # Scoreboard
        self._p1_label.config(
            text=f"{self._p1_label.cget('text').split(chr(10))[0]}\n{self._state.p1_points} pts"
        )
        self._p2_label.config(
            text=f"{self._p2_label.cget('text').split(chr(10))[0]}\n{self._state.p2_points} pts"
        )
        turn_str = f"Turn: P{self._state.turn}"
        self._turn_label.config(text=turn_str)

    def _set_buttons_enabled(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        # Only show human buttons in human_vs_ai mode
        if self._mode == "human_vs_ai" and self._p1_config.kind == "human":
            self._left_btn.config(state=state)
            self._right_btn.config(state=state)

    def _set_status(self, msg: str):
        self._status_label.config(text=msg, fg=GREEN)

    def _log(self, msg: str):
        self._log_text.config(state=tk.NORMAL)
        self._log_text.insert(tk.END, msg + "\n")
        self._log_text.see(tk.END)
        self._log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self._log_text.config(state=tk.NORMAL)
        self._log_text.delete("1.0", tk.END)
        self._log_text.config(state=tk.DISABLED)

    def get_game_record(self) -> GameRecord:
        """Return the GameRecord for the most recently completed game."""
        return self._game_record

    def _back(self):
        self._on_back()
