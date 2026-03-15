from __future__ import annotations

from typing import List, Optional

from game.state import GameState
from game.rules import apply_move, get_legal_moves, is_terminal


class GameTreeNode:
    __slots__ = ("state", "move", "parent", "children", "value", "depth")

    def __init__(
        self,
        state: GameState,
        move: Optional[str] = None,
        parent: Optional["GameTreeNode"] = None,
        depth: int = 0,
    ) -> None:
        self.state: GameState = state
        self.move: Optional[str] = move
        self.parent: Optional["GameTreeNode"] = parent
        self.children: List["GameTreeNode"] = []
        self.value: Optional[float] = None
        self.depth: int = depth

    def expand(self, nodes_generated_counter: Optional[list] = None) -> List["GameTreeNode"]:
        if self.children:
            return self.children

        legal_moves = get_legal_moves(self.state)
        for move in legal_moves:
            child_state = apply_move(self.state, move)
            self.children.append(
                GameTreeNode(
                    state=child_state,
                    move=move,
                    parent=self,
                    depth=self.depth + 1,
                )
            )

            if nodes_generated_counter is not None:
                nodes_generated_counter[0] += 1

        return self.children

    def is_terminal(self) -> bool:
        return is_terminal(self.state)

    def best_child(self, maximizing: bool) -> Optional["GameTreeNode"]:
        if not self.children:
            return None

        if maximizing:
            return max(
                self.children,
                key=lambda c: c.value if c.value is not None else float("-inf"),
            )

        return min(
            self.children,
            key=lambda c: c.value if c.value is not None else float("inf"),
        )

    def __repr__(self) -> str:
        return (
            f"GameTreeNode(move={self.move!r}, depth={self.depth}, "
            f"value={self.value}, state={self.state})"
        )
