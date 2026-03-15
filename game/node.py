from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from game.state import GameState
from game.rules import get_legal_moves, apply_move

if TYPE_CHECKING:
    from experiments.runner import MoveStats


class GameTreeNode:
    __slots__ = ("state", "move", "parent", "children", "value", "depth")

    def __init__(
        self,
        state: GameState,
        move: Optional[str] = None,
        parent: Optional["GameTreeNode"] = None,
        depth: int = 0,
    ) -> None:
        self.state:    GameState            = state
        self.move:     Optional[str]        = move
        self.parent:   Optional[GameTreeNode] = parent
        self.children: List[GameTreeNode]   = []
        self.value:    Optional[float]      = None
        self.depth:    int                  = depth

    def expand(self, nodes_generated_counter: Optional[list] = None) -> List["GameTreeNode"]:
        if self.children:
            return self.children

        legal_moves = get_legal_moves(self.state)
        for move in legal_moves:
            child_state = apply_move(self.state, move)
            child = GameTreeNode(
                state=child_state,
                move=move,
                parent=self,
                depth=self.depth + 1,
            )
            self.children.append(child)

            if nodes_generated_counter is not None:
                nodes_generated_counter[0] += 1

        return self.children


    def is_terminal(self) -> bool:
        from game.rules import is_terminal
        return is_terminal(self.state)

    def __repr__(self) -> str:
        return (
            f"GameTreeNode(move={self.move!r}, depth={self.depth}, "
            f"value={self.value}, state={self.state})"
        )
