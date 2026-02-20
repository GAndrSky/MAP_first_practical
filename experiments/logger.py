"""
experiments/logger.py
=====================
GameLogger — exports game records to CSV and JSON formats.

CSV output (summary, one row per game):
    game_id, initial_sequence, starting_player, p1_algo, p1_depth,
    p2_algo, p2_depth, winner, final_p1_points, final_p2_points,
    total_moves, total_time_s,
    p1_nodes_generated, p1_nodes_evaluated, p1_total_time_s,
    p2_nodes_generated, p2_nodes_evaluated, p2_total_time_s

JSON output (detailed, one object per game with full move list):
    All fields from GameRecord + per-move detail.

No external dependencies — uses only stdlib json and csv.
"""

import csv
import json
import os
from typing import List

from experiments.runner import GameRecord, MoveStats


class GameLogger:
    """
    Serialises a list of GameRecord objects to CSV and/or JSON.

    Usage
    -----
    GameLogger.export_csv(records, "results/summary.csv")
    GameLogger.export_json(records, "results/detail.json")
    """

    # ── CSV export ─────────────────────────────────────────────────────────────

    @staticmethod
    def export_csv(records: List[GameRecord], path: str) -> None:
        """
        Write a summary CSV: one row per game.

        Parameters
        ----------
        records : list[GameRecord]
        path    : str  — file path (created/overwritten)
        """
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        fieldnames = [
            "game_id", "initial_sequence", "starting_player",
            "p1_algo", "p1_depth", "p2_algo", "p2_depth",
            "winner", "final_p1_points", "final_p2_points",
            "total_moves", "total_time_s",
            "p1_nodes_generated", "p1_nodes_evaluated", "p1_total_time_s",
            "p2_nodes_generated", "p2_nodes_evaluated", "p2_total_time_s",
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for rec in records:
                # Aggregate per-player stats from move records
                p1_gen = p1_eval = p2_gen = p2_eval = 0
                p1_time = p2_time = 0.0

                for mr in rec.moves:
                    if mr.player_turn == 1:
                        p1_gen  += mr.nodes_generated
                        p1_eval += mr.nodes_evaluated
                        p1_time += mr.time_s
                    else:
                        p2_gen  += mr.nodes_generated
                        p2_eval += mr.nodes_evaluated
                        p2_time += mr.time_s

                writer.writerow({
                    "game_id":            rec.game_id,
                    "initial_sequence":   list(rec.initial_sequence),
                    "starting_player":    rec.starting_player,
                    "p1_algo":            rec.p1_config.kind,
                    "p1_depth":           rec.p1_config.depth,
                    "p2_algo":            rec.p2_config.kind,
                    "p2_depth":           rec.p2_config.depth,
                    "winner":             rec.winner,
                    "final_p1_points":    rec.final_p1_points,
                    "final_p2_points":    rec.final_p2_points,
                    "total_moves":        len(rec.moves),
                    "total_time_s":       round(rec.total_time_s, 6),
                    "p1_nodes_generated": p1_gen,
                    "p1_nodes_evaluated": p1_eval,
                    "p1_total_time_s":    round(p1_time, 6),
                    "p2_nodes_generated": p2_gen,
                    "p2_nodes_evaluated": p2_eval,
                    "p2_total_time_s":    round(p2_time, 6),
                })

    # ── JSON export ────────────────────────────────────────────────────────────

    @staticmethod
    def export_json(records: List[GameRecord], path: str) -> None:
        """
        Write detailed JSON: one object per game, with full move list.

        Parameters
        ----------
        records : list[GameRecord]
        path    : str  — file path (created/overwritten)
        """
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

        data = []
        for rec in records:
            moves_data = []
            for mr in rec.moves:
                moves_data.append({
                    "move_index":       mr.move_index,
                    "player_turn":      mr.player_turn,
                    "action":           mr.action,
                    "value_taken":      mr.value_taken,
                    "p1_points_after":  mr.p1_points_after,
                    "p2_points_after":  mr.p2_points_after,
                    "sequence_after":   list(mr.sequence_after),
                    "time_s":           round(mr.time_s, 6),
                    "nodes_generated":  mr.nodes_generated,
                    "nodes_evaluated":  mr.nodes_evaluated,
                    "algorithm":        mr.algorithm,
                })

            data.append({
                "game_id":          rec.game_id,
                "initial_sequence": list(rec.initial_sequence),
                "starting_player":  rec.starting_player,
                "p1_config": {
                    "player_id": rec.p1_config.player_id,
                    "kind":      rec.p1_config.kind,
                    "depth":     rec.p1_config.depth,
                },
                "p2_config": {
                    "player_id": rec.p2_config.player_id,
                    "kind":      rec.p2_config.kind,
                    "depth":     rec.p2_config.depth,
                },
                "winner":           rec.winner,
                "final_p1_points":  rec.final_p1_points,
                "final_p2_points":  rec.final_p2_points,
                "total_time_s":     round(rec.total_time_s, 6),
                "moves":            moves_data,
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
