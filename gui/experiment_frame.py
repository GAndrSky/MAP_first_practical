"""
gui/experiment_frame.py
=======================
Batch experiment tab: configure K games, algorithms, depth per player,
run in a background thread, display results, and export CSV/JSON.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from game.state import MIN_N, MAX_N
from experiments.runner import BatchRunner, PlayerConfig
from experiments.logger import GameLogger


# ── Colour palette ─────────────────────────────────────────────────────────────
BG      = "#1e1e2e"
SURFACE = "#313244"
OVERLAY = "#45475a"
BLUE    = "#89b4fa"
GREEN   = "#a6e3a1"
RED     = "#f38ba8"
YELLOW  = "#f9e2af"
TEXT    = "#cdd6f4"
SUBTEXT = "#a6adc8"


class ExperimentFrame(tk.Frame):
    """Batch experiment runner UI."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._records = []
        self._last_p1 = None
        self._last_p2 = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        tk.Label(
            self, text="Batch Experiment Runner",
            font=("Segoe UI", 14, "bold"), fg=TEXT, bg=BG,
        ).pack(pady=(16, 10))

        # ── Config panel ───────────────────────────────────────────────────────
        cfg_frame = tk.Frame(self, bg=SURFACE, padx=16, pady=12)
        cfg_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Row 0: K and N
        tk.Label(cfg_frame, text="Games (K):", fg=TEXT, bg=SURFACE,
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, pady=6)
        self._k_var = tk.IntVar(value=10)
        tk.Spinbox(cfg_frame, from_=1, to=1000, textvariable=self._k_var,
                   width=6, font=("Segoe UI", 10), bg=OVERLAY, fg=TEXT,
                   buttonbackground=OVERLAY, insertbackground=TEXT,
                   ).grid(row=0, column=1, padx=8, pady=6, sticky=tk.W)

        tk.Label(cfg_frame, text="Seq length (N):", fg=TEXT, bg=SURFACE,
                 font=("Segoe UI", 10)).grid(row=0, column=2, padx=(20, 0), sticky=tk.W)
        self._n_var = tk.IntVar(value=20)
        tk.Spinbox(cfg_frame, from_=MIN_N, to=MAX_N, textvariable=self._n_var,
                   width=5, font=("Segoe UI", 10), bg=OVERLAY, fg=TEXT,
                   buttonbackground=OVERLAY, insertbackground=TEXT,
                   ).grid(row=0, column=3, padx=8, pady=6, sticky=tk.W)

        tk.Label(cfg_frame, text="Seed:", fg=TEXT, bg=SURFACE,
                 font=("Segoe UI", 10)).grid(row=0, column=4, padx=(20, 0), sticky=tk.W)
        self._seed_var = tk.StringVar(value="42")
        tk.Entry(cfg_frame, textvariable=self._seed_var, width=6,
                 font=("Segoe UI", 10), bg=OVERLAY, fg=TEXT,
                 insertbackground=TEXT).grid(row=0, column=5, padx=8, pady=6)

        # Row 1: P1 config
        self._p1_algo_var, self._p1_depth_var = self._add_player_row(
            cfg_frame, row=1, label="Player 1:", default_algo="minimax", default_depth=5
        )
        # Row 2: P2 config
        self._p2_algo_var, self._p2_depth_var = self._add_player_row(
            cfg_frame, row=2, label="Player 2:", default_algo="alphabeta", default_depth=5
        )

        # ── Run button + progress ──────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill=tk.X, padx=20, pady=(0, 8))

        self._run_btn = tk.Button(
            btn_row, text="▶  Run Experiments",
            command=self._run_experiments,
            bg=GREEN, fg=BG, activebackground="#94e2d5",
            font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=14, pady=6,
        )
        self._run_btn.pack(side=tk.LEFT)

        self._progress_var = tk.StringVar(value="")
        tk.Label(btn_row, textvariable=self._progress_var,
                 fg=YELLOW, bg=BG, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=16)

        # ── Export buttons ─────────────────────────────────────────────────────
        export_row = tk.Frame(self, bg=BG)
        export_row.pack(fill=tk.X, padx=20, pady=(0, 8))

        tk.Button(
            export_row, text="💾  Export CSV",
            command=self._export_csv,
            bg=BLUE, fg=BG, activebackground="#74c7ec",
            font=("Segoe UI", 10), relief=tk.FLAT, padx=12, pady=4,
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            export_row, text="💾  Export JSON",
            command=self._export_json,
            bg=BLUE, fg=BG, activebackground="#74c7ec",
            font=("Segoe UI", 10), relief=tk.FLAT, padx=12, pady=4,
        ).pack(side=tk.LEFT)

        # ── Results text area ──────────────────────────────────────────────────
        tk.Label(self, text="Results:", fg=SUBTEXT, bg=BG,
                 font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=20)

        result_outer = tk.Frame(self, bg=BG)
        result_outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=(4, 16))

        scrollbar = tk.Scrollbar(result_outer)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._result_text = tk.Text(
            result_outer, state=tk.DISABLED,
            bg=SURFACE, fg=TEXT, font=("Consolas", 9),
            yscrollcommand=scrollbar.set, relief=tk.FLAT,
            selectbackground=OVERLAY,
        )
        self._result_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._result_text.yview)

    def _add_player_row(self, parent, row, label, default_algo, default_depth):
        """Add an algorithm + depth row for one player. Returns (algo_var, depth_var)."""
        tk.Label(parent, text=label, fg=TEXT, bg=SURFACE,
                 font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=6)

        algo_var = tk.StringVar(value=default_algo)
        tk.Radiobutton(parent, text="Minimax", variable=algo_var, value="minimax",
                       fg=TEXT, bg=SURFACE, selectcolor=OVERLAY,
                       activebackground=SURFACE, activeforeground=TEXT,
                       font=("Segoe UI", 10)).grid(row=row, column=1, padx=6)
        tk.Radiobutton(parent, text="Alpha-Beta", variable=algo_var, value="alphabeta",
                       fg=TEXT, bg=SURFACE, selectcolor=OVERLAY,
                       activebackground=SURFACE, activeforeground=TEXT,
                       font=("Segoe UI", 10)).grid(row=row, column=2, padx=6)

        tk.Label(parent, text="Depth:", fg=TEXT, bg=SURFACE,
                 font=("Segoe UI", 10)).grid(row=row, column=3, padx=(20, 4))
        depth_var = tk.IntVar(value=default_depth)
        tk.Scale(parent, from_=1, to=12, orient=tk.HORIZONTAL,
                 variable=depth_var, bg=SURFACE, fg=TEXT,
                 troughcolor=OVERLAY, highlightthickness=0,
                 font=("Segoe UI", 8), length=160,
                 ).grid(row=row, column=4, columnspan=2, padx=4, sticky=tk.W)

        return algo_var, depth_var

    # ── Actions ────────────────────────────────────────────────────────────────

    def _run_experiments(self):
        """Validate inputs and launch batch run in a background thread."""
        try:
            K = self._k_var.get()
            n = self._n_var.get()
            seed_str = self._seed_var.get().strip()
            seed = int(seed_str) if seed_str else None
        except (tk.TclError, ValueError):
            messagebox.showerror("Input Error", "Please enter valid integers for K, N, and Seed.")
            return

        if K < 1:
            messagebox.showerror("Input Error", "K must be at least 1.")
            return
        if not (MIN_N <= n <= MAX_N):
            messagebox.showerror("Input Error", f"N must be in [{MIN_N}, {MAX_N}].")
            return

        p1_cfg = PlayerConfig(player_id=1, kind=self._p1_algo_var.get(),
                              depth=self._p1_depth_var.get())
        p2_cfg = PlayerConfig(player_id=2, kind=self._p2_algo_var.get(),
                              depth=self._p2_depth_var.get())
        self._last_p1 = p1_cfg
        self._last_p2 = p2_cfg

        self._run_btn.config(state=tk.DISABLED)
        self._append_result(f"\nStarting {K} games: {p1_cfg} vs {p2_cfg}  (N={n})\n")

        def task():
            runner = BatchRunner()
            records, batch_stats = runner.run(
                K=K, n=n,
                p1_config=p1_cfg, p2_config=p2_cfg,
                seed=seed,
                progress_callback=self._on_progress,
            )
            self._records = records
            # Update UI in main thread
            self.after(0, lambda: self._on_done(batch_stats, p1_cfg, p2_cfg))

        threading.Thread(target=task, daemon=True).start()

    def _on_progress(self, done: int, total: int):
        """Called from background thread — schedule UI update via after()."""
        self.after(0, lambda: self._progress_var.set(f"  {done}/{total} games completed…"))

    def _on_done(self, batch_stats, p1_cfg, p2_cfg):
        """Called in main thread when all games finish."""
        self._progress_var.set(f"  Done!")
        self._run_btn.config(state=tk.NORMAL)
        summary = batch_stats.summary_str(p1_cfg, p2_cfg)
        self._append_result(summary + "\n")

    def _append_result(self, text: str):
        self._result_text.config(state=tk.NORMAL)
        self._result_text.insert(tk.END, text)
        self._result_text.see(tk.END)
        self._result_text.config(state=tk.DISABLED)

    # ── Export ─────────────────────────────────────────────────────────────────

    def _export_csv(self):
        if not self._records:
            messagebox.showwarning("No Data", "Run experiments first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="experiment_summary.csv",
            title="Export Summary CSV",
        )
        if path:
            GameLogger.export_csv(self._records, path)
            self._append_result(f"CSV exported → {path}\n")
            messagebox.showinfo("Export", f"CSV saved to:\n{path}")

    def _export_json(self):
        if not self._records:
            messagebox.showwarning("No Data", "Run experiments first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="experiment_detail.json",
            title="Export Detail JSON",
        )
        if path:
            GameLogger.export_json(self._records, path)
            self._append_result(f"JSON exported → {path}\n")
            messagebox.showinfo("Export", f"JSON saved to:\n{path}")
