"""
gui/app.py
==========
Root Tkinter window with a ttk.Notebook containing two tabs:
  1. Game tab    — SetupFrame → GameFrame flow
  2. Experiments — ExperimentFrame (batch runner)
"""

import tkinter as tk
from tkinter import ttk

from gui.setup_frame      import SetupFrame
from gui.game_frame       import GameFrame
from gui.experiment_frame import ExperimentFrame


# ── Colour palette ─────────────────────────────────────────────────────────────
BG = "#1e1e2e"


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Number Sequence Game  •  Minimax & Alpha-Beta")
        self.geometry("820x680")
        self.minsize(720, 560)
        self.configure(bg=BG)
        self._configure_styles()
        self._build_ui()

    # ── Style ──────────────────────────────────────────────────────────────────

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background="#313244", foreground="#cdd6f4",
                         font=("Segoe UI", 10, "bold"), padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", "#89b4fa")],
                  foreground=[("selected", "#1e1e2e")])

    # ── UI ─────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # ── Game tab ───────────────────────────────────────────────────────────
        self._game_tab = tk.Frame(notebook, bg=BG)
        notebook.add(self._game_tab, text="  🎮  Game  ")

        # We show either the SetupFrame or the GameFrame inside the game tab
        self._setup_frame = SetupFrame(
            self._game_tab, on_start=self._start_game
        )
        self._game_frame = GameFrame(
            self._game_tab, on_back=self._show_setup
        )

        # Initially show setup
        self._show_setup()

        # ── Experiments tab ────────────────────────────────────────────────────
        exp_tab = tk.Frame(notebook, bg=BG)
        notebook.add(exp_tab, text="  🧪  Experiments  ")

        ExperimentFrame(exp_tab).pack(fill=tk.BOTH, expand=True)

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _show_setup(self):
        """Show the setup frame, hide the game frame."""
        self._game_frame.pack_forget()
        self._setup_frame.pack(fill=tk.BOTH, expand=True)

    def _start_game(self, config: dict):
        """Transition from SetupFrame to GameFrame with the given config."""
        self._setup_frame.pack_forget()
        self._game_frame.pack(fill=tk.BOTH, expand=True)
        self._game_frame.start_game(config)
