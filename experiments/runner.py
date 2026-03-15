from __future__ import annotations
import time
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from game.state import GameState, make_initial_state
from game.rules import generate_sequence, apply_move, is_terminal, get_winner, MOVE_LEFT, MOVE_RIGHT
from ai.dispatcher import get_best_ai_move

@dataclass
class MoveStats:
    nodes_generated:  int   = 0
    nodes_evaluated:  int   = 0
    time_s:           float = 0.0  

    def __add__(self, other: "MoveStats") -> "MoveStats":
        return MoveStats(
            nodes_generated  = self.nodes_generated  + other.nodes_generated,
            nodes_evaluated  = self.nodes_evaluated  + other.nodes_evaluated,
            time_s           = self.time_s           + other.time_s,
        )


@dataclass
class MoveRecord:
    move_index:       int
    player_turn:      int          
    action:           str          
    value_taken:      int          
    p1_points_after:  int
    p2_points_after:  int
    sequence_after:   tuple
    time_s:           float
    nodes_generated:  int = 0      
    nodes_evaluated:  int = 0
    algorithm:        str = ""     


@dataclass
class GameRecord:
    game_id:          int
    initial_sequence: tuple
    starting_player:  int
    p1_config:        "PlayerConfig"
    p2_config:        "PlayerConfig"
    moves:            List[MoveRecord] = field(default_factory=list)
    winner:           int = -1     
    final_p1_points:  int = 0
    final_p2_points:  int = 0
    total_time_s:     float = 0.0


@dataclass
class PlayerConfig:
    player_id:  int           
    kind:       str           
    depth:      int = 5       

    def __str__(self) -> str:
        if self.kind == "human":
            return f"Human(P{self.player_id})"
        return f"{self.kind.capitalize()}(P{self.player_id}, d={self.depth})"

@dataclass
class BatchStats:
    total_games:      int = 0
    p1_wins:          int = 0
    p2_wins:          int = 0
    draws:            int = 0

    p1_total_stats:   MoveStats = field(default_factory=MoveStats)
    p2_total_stats:   MoveStats = field(default_factory=MoveStats)
    p1_move_count:    int = 0
    p2_move_count:    int = 0

    def record_winner(self, winner: int) -> None:
        self.total_games += 1
        if winner == 1:
            self.p1_wins += 1
        elif winner == 2:
            self.p2_wins += 1
        else:
            self.draws += 1

    def add_move_stats(self, player_id: int, stats: MoveStats) -> None:
        if player_id == 1:
            self.p1_total_stats = self.p1_total_stats + stats
            self.p1_move_count += 1
        else:
            self.p2_total_stats = self.p2_total_stats + stats
            self.p2_move_count += 1

    @property
    def p1_avg_time(self) -> float:
        return self.p1_total_stats.time_s / self.p1_move_count if self.p1_move_count else 0.0

    @property
    def p2_avg_time(self) -> float:
        return self.p2_total_stats.time_s / self.p2_move_count if self.p2_move_count else 0.0

    def summary_str(self, p1_cfg: PlayerConfig, p2_cfg: PlayerConfig) -> str:
        lines = [
            f"{'─'*50}",
            f"  Batch Results  ({self.total_games} games)",
            f"{'─'*50}",
            f"  Player 1 ({p1_cfg}):  {self.p1_wins} wins",
            f"  Player 2 ({p2_cfg}):  {self.p2_wins} wins",
            f"  Draws:               {self.draws}",
            f"{'─'*50}",
            f"  P1 nodes generated:  {self.p1_total_stats.nodes_generated}",
            f"  P1 nodes evaluated:  {self.p1_total_stats.nodes_evaluated}",
            f"  P1 avg time/move:    {self.p1_avg_time*1000:.3f} ms",
            f"  P2 nodes generated:  {self.p2_total_stats.nodes_generated}",
            f"  P2 nodes evaluated:  {self.p2_total_stats.nodes_evaluated}",
            f"  P2 avg time/move:    {self.p2_avg_time*1000:.3f} ms",
            f"{'─'*50}",
        ]
        return "\n".join(lines)

class BatchRunner:
    def run(
        self,
        K: int,
        n: int,
        p1_config: PlayerConfig,
        p2_config: PlayerConfig,
        seed: Optional[int] = None,
        progress_callback=None,
    ) -> tuple:
        rng = random.Random(seed)
        records: List[GameRecord] = []
        batch_stats = BatchStats()

        for game_idx in range(K):
            sequence = generate_sequence(n, rng=rng)
            starting_player = 1 + (game_idx % 2)
            record = self._run_one_game(
                game_id=game_idx,
                sequence=sequence,
                starting_player=starting_player,
                p1_config=p1_config,
                p2_config=p2_config,
            )
            records.append(record)
            batch_stats.record_winner(record.winner)

            for move_rec in record.moves:
                ms = MoveStats(
                    nodes_generated=move_rec.nodes_generated,
                    nodes_evaluated=move_rec.nodes_evaluated,
                    time_s=move_rec.time_s,
                )
                if move_rec.nodes_generated > 0 or move_rec.nodes_evaluated > 0:
                    batch_stats.add_move_stats(move_rec.player_turn, ms)

            if progress_callback:
                progress_callback(game_idx + 1, K)

        return records, batch_stats

    def _run_one_game(
        self,
        game_id: int,
        sequence: tuple,
        starting_player: int,
        p1_config: PlayerConfig,
        p2_config: PlayerConfig,
    ) -> GameRecord:
        state = make_initial_state(sequence, first_player=starting_player)
        record = GameRecord(
            game_id=game_id,
            initial_sequence=sequence,
            starting_player=starting_player,
            p1_config=p1_config,
            p2_config=p2_config,
        )
        move_idx = 0
        t_game_start = time.perf_counter()

        while not is_terminal(state):
            current_player = state.turn
            cfg = p1_config if current_player == 1 else p2_config

            t_start = time.perf_counter()
            move, move_stats = get_best_ai_move(state, cfg)
            t_end = time.perf_counter()
            move_stats.time_s = t_end - t_start

            value_taken = state.sequence[0] if move == MOVE_LEFT else state.sequence[-1]

            state = apply_move(state, move)

            record.moves.append(MoveRecord(
                move_index=move_idx,
                player_turn=current_player,
                action=move,
                value_taken=value_taken,
                p1_points_after=state.p1_points,
                p2_points_after=state.p2_points,
                sequence_after=state.sequence,
                time_s=move_stats.time_s,
                nodes_generated=move_stats.nodes_generated,
                nodes_evaluated=move_stats.nodes_evaluated,
                algorithm=cfg.kind,
            ))
            move_idx += 1

        record.winner = get_winner(state)
        record.final_p1_points = state.p1_points
        record.final_p2_points = state.p2_points
        record.total_time_s = time.perf_counter() - t_game_start
        return record


