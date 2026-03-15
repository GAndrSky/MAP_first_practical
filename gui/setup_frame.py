import tkinter as tk
from tkinter import ttk, messagebox
from game.rules import generate_sequence
from game.state import MIN_N, MAX_N


class SetupFrame(tk.Frame):
    def __init__(self, parent, on_start, **kwargs):
        super().__init__(parent, **kwargs)
        self._on_start = on_start
        self._sequence = None
        self._build_ui()

    def _build_ui(self):
        self.configure(bg="#1e1e2e", padx=20, pady=20)

        tk.Label(
            self, text="Number Sequence Game  •  AI Project",
            font=("Segoe UI", 16, "bold"), fg="#cdd6f4", bg="#1e1e2e"
        ).grid(row=0, column=0, columnspan=4, pady=(0, 18))

        self._mode_var = tk.StringVar(value="human_vs_ai")

        mode_frame = tk.LabelFrame(
            self, text=" Game Mode ", fg="#89b4fa", bg="#1e1e2e",
            font=("Segoe UI", 10, "bold"), bd=1, relief=tk.GROOVE
        )
        mode_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 14), padx=4)

        for col, (label, val) in enumerate([
            ("Human vs AI", "human_vs_ai"),
            ("AI vs AI",    "ai_vs_ai"),
        ]):
            tk.Radiobutton(
                mode_frame, text=label, variable=self._mode_var, value=val,
                command=self._on_mode_change,
                bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                activebackground="#1e1e2e", activeforeground="#cdd6f4",
                font=("Segoe UI", 10),
            ).pack(side=tk.LEFT, padx=18, pady=6)

        seq_frame = tk.LabelFrame(
            self, text=" Sequence ", fg="#89b4fa", bg="#1e1e2e",
            font=("Segoe UI", 10, "bold"), bd=1, relief=tk.GROOVE
        )
        seq_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 14), padx=4)

        tk.Label(seq_frame, text=f"N  ({MIN_N}–{MAX_N}):", fg="#cdd6f4",
                 bg="#1e1e2e", font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=8)

        self._n_var = tk.IntVar(value=20)
        self._n_spin = tk.Spinbox(
            seq_frame, from_=MIN_N, to=MAX_N, textvariable=self._n_var,
            width=5, font=("Segoe UI", 10), bg="#313244", fg="#cdd6f4",
            buttonbackground="#45475a", insertbackground="#cdd6f4",
        )
        self._n_spin.grid(row=0, column=1, padx=6, pady=8)

        self._gen_btn = tk.Button(
            seq_frame, text="🎲  Generate Sequence", command=self._generate_sequence,
            bg="#89b4fa", fg="#1e1e2e", activebackground="#74c7ec",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, pady=4,
        )
        self._gen_btn.grid(row=0, column=2, padx=10, pady=8)

        self._seq_label = tk.Label(
            seq_frame, text="No sequence yet", wraplength=500,
            fg="#a6e3a1", bg="#1e1e2e", font=("Segoe UI", 9),
        )
        self._seq_label.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 8))

        self._p1_frame = self._build_player_frame(
            row=3, label="Player 1 (you)", is_human_mode=True,
            algo_default="minimax", depth_default=5,
        )

        self._p2_frame = self._build_player_frame(
            row=4, label="Player 2 (AI)", is_human_mode=False,
            algo_default="alphabeta", depth_default=5,
        )

        self._start_player_frame = tk.LabelFrame(
            self, text=" Who Goes First? ", fg="#89b4fa", bg="#1e1e2e",
            font=("Segoe UI", 10, "bold"), bd=1, relief=tk.GROOVE
        )
        self._start_player_frame.grid(row=5, column=0, columnspan=4,
                                      sticky="ew", pady=(0, 14), padx=4)

        self._first_var = tk.StringVar(value="human")
        for col, (label, val) in enumerate([("Human first", "human"), ("AI first", "ai")]):
            tk.Radiobutton(
                self._start_player_frame, text=label,
                variable=self._first_var, value=val,
                bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                activebackground="#1e1e2e", activeforeground="#cdd6f4",
                font=("Segoe UI", 10),
            ).pack(side=tk.LEFT, padx=18, pady=6)

        tk.Button(
            self, text="▶   Start Game", command=self._start_game,
            bg="#a6e3a1", fg="#1e1e2e", activebackground="#94e2d5",
            font=("Segoe UI", 12, "bold"), relief=tk.FLAT, padx=16, pady=8,
        ).grid(row=6, column=0, columnspan=4, pady=10)

        self._on_mode_change()

    def _build_player_frame(self, row, label, is_human_mode, algo_default, depth_default):
        frame = tk.LabelFrame(
            self, text=f" {label} ", fg="#89b4fa", bg="#1e1e2e",
            font=("Segoe UI", 10, "bold"), bd=1, relief=tk.GROOVE,
        )
        frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(0, 10), padx=4)

        data = {}

        if is_human_mode:
            data["kind_label"] = tk.Label(
                frame, text="Human (you)", fg="#cdd6f4", bg="#1e1e2e",
                font=("Segoe UI", 10, "italic"),
            )
            data["kind_label"].grid(row=0, column=0, columnspan=4, pady=8)
        else:
            tk.Label(frame, text="Algorithm:", fg="#cdd6f4",
                     bg="#1e1e2e", font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=8)

            data["algo_var"] = tk.StringVar(value=algo_default)
            for i, (txt, val) in enumerate([("Minimax", "minimax"), ("Alpha-Beta", "alphabeta")]):
                tk.Radiobutton(
                    frame, text=txt, variable=data["algo_var"], value=val,
                    bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                    activebackground="#1e1e2e", activeforeground="#cdd6f4",
                    font=("Segoe UI", 10),
                ).grid(row=0, column=i + 1, padx=10, pady=8)

        if not is_human_mode or True:
            tk.Label(frame, text="Depth:", fg="#cdd6f4",
                     bg="#1e1e2e", font=("Segoe UI", 10)).grid(row=1, column=0, padx=10, pady=4)

            data["depth_var"] = tk.IntVar(value=depth_default)
            slider = tk.Scale(
                frame, from_=1, to=12, orient=tk.HORIZONTAL,
                variable=data["depth_var"],
                bg="#1e1e2e", fg="#cdd6f4", troughcolor="#45475a",
                highlightthickness=0, font=("Segoe UI", 9),
                length=220,
            )
            slider.grid(row=1, column=1, columnspan=3, padx=6, pady=4, sticky="w")

        frame._data = data
        return frame

    def _on_mode_change(self):
        mode = self._mode_var.get()
        if mode == "human_vs_ai":
            self._start_player_frame.grid()
            for widget in self._p1_frame.winfo_children():
                widget.destroy()
            self._p1_frame.configure(text=" Player 1 (Human — you) ")
            tk.Label(
                self._p1_frame, text="Human (you)", fg="#cdd6f4",
                bg="#1e1e2e", font=("Segoe UI", 10, "italic"),
            ).pack(pady=10)
        else:
            self._start_player_frame.grid_remove()
            for widget in self._p1_frame.winfo_children():
                widget.destroy()
            self._p1_frame.configure(text=" Player 1 (AI) ")
            self._p1_frame._data = {}
            d = self._p1_frame._data
            tk.Label(self._p1_frame, text="Algorithm:", fg="#cdd6f4",
                     bg="#1e1e2e", font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=8)
            d["algo_var"] = tk.StringVar(value="minimax")
            for i, (txt, val) in enumerate([("Minimax", "minimax"), ("Alpha-Beta", "alphabeta")]):
                tk.Radiobutton(
                    self._p1_frame, text=txt, variable=d["algo_var"], value=val,
                    bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244",
                    activebackground="#1e1e2e", activeforeground="#cdd6f4",
                    font=("Segoe UI", 10),
                ).grid(row=0, column=i + 1, padx=10, pady=8)
            tk.Label(self._p1_frame, text="Depth:", fg="#cdd6f4",
                     bg="#1e1e2e", font=("Segoe UI", 10)).grid(row=1, column=0, padx=10, pady=4)
            d["depth_var"] = tk.IntVar(value=5)
            tk.Scale(
                self._p1_frame, from_=1, to=12, orient=tk.HORIZONTAL,
                variable=d["depth_var"], bg="#1e1e2e", fg="#cdd6f4",
                troughcolor="#45475a", highlightthickness=0,
                font=("Segoe UI", 9), length=220,
            ).grid(row=1, column=1, columnspan=3, padx=6, pady=4, sticky="w")

    def _generate_sequence(self):
        try:
            n = self._n_var.get()
        except tk.TclError:
            messagebox.showerror("Invalid N", "Please enter a valid integer for N.")
            return

        if not (MIN_N <= n <= MAX_N):
            messagebox.showerror(
                "Invalid N",
                f"N must be between {MIN_N} and {MAX_N}. Got {n}."
            )
            return

        self._sequence = generate_sequence(n)
        self._seq_label.config(text="  ".join(str(v) for v in self._sequence))

    def _start_game(self):
        if self._sequence is None:
            messagebox.showwarning("No Sequence", "Please generate a sequence first.")
            return

        mode = self._mode_var.get()

        if mode == "human_vs_ai":
            first_player = 1 if self._first_var.get() == "human" else 2
            p2_data = self._p2_frame._data
            config = {
                "mode":           "human_vs_ai",
                "sequence":       self._sequence,
                "first_player":   first_player,
                "p1_kind":        "human",
                "p1_depth":       0,
                "p2_kind":        p2_data["algo_var"].get(),
                "p2_depth":       p2_data["depth_var"].get(),
            }
        else:
            p1_data = self._p1_frame._data
            p2_data = self._p2_frame._data
            config = {
                "mode":           "ai_vs_ai",
                "sequence":       self._sequence,
                "first_player":   1,
                "p1_kind":        p1_data["algo_var"].get(),
                "p1_depth":       p1_data["depth_var"].get(),
                "p2_kind":        p2_data["algo_var"].get(),
                "p2_depth":       p2_data["depth_var"].get(),
            }
        self._on_start(config)
