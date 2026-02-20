"""
main.py
=======
Entry point for the Number Sequence Game AI project.

How to run:
-----------
  python main.py

Requirements:
  - Python 3.9+  (uses tuple type hints, dataclasses)
  - No external packages required — only stdlib (tkinter, json, csv, time, random)

Project structure:
  game/        – GameState, GameTreeNode, rules
  ai/          – Minimax, Alpha-Beta, heuristic
  experiments/ – BatchRunner, GameLogger (CSV + JSON export)
  gui/         – Tkinter GUI (App, SetupFrame, GameFrame, ExperimentFrame)
"""

import sys
import os

# Ensure the project root is on sys.path when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import App


if __name__ == "__main__":
    app = App()
    app.mainloop()
