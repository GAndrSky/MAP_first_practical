import tkinter as tk
from tkinter import ttk

from gui.setup_frame      import SetupFrame
from gui.game_frame       import GameFrame
from gui.experiment_frame import ExperimentFrame

BG = "#1e1e2e"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Number Sequence Game  •  Minimax & Alpha-Beta")
        self.geometry("820x680")
        self.minsize(720, 560)
        self.configure(bg=BG)
        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background="#313244", foreground="#cdd6f4",
                         font=("Segoe UI", 10, "bold"), padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", "#89b4fa")],
                  foreground=[("selected", "#1e1e2e")])

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self._game_tab = tk.Frame(notebook, bg=BG)
        notebook.add(self._game_tab, text="  🎮  Game  ")

        self._setup_frame = SetupFrame(
            self._game_tab, on_start=self._start_game
        )
        self._game_frame = GameFrame(
            self._game_tab, on_back=self._show_setup
        )

        self._show_setup()

        exp_tab = tk.Frame(notebook, bg=BG)
        notebook.add(exp_tab, text="  🧪  Experiments  ")

        ExperimentFrame(exp_tab).pack(fill=tk.BOTH, expand=True)

    def _show_setup(self):
        self._game_frame.pack_forget()
        self._setup_frame.pack(fill=tk.BOTH, expand=True)

    def _start_game(self, config: dict):
        self._setup_frame.pack_forget()
        self._game_frame.pack(fill=tk.BOTH, expand=True)
        self._game_frame.start_game(config)
