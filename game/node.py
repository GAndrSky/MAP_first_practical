"""
game/node.py
============
GameTreeNode — the explicit node structure for the Minimax/Alpha-Beta tree.

Each node holds:
  • state      – the GameState at this node
  • move       – the move that led FROM the parent TO this node (None at root)
  • parent     – reference to the parent node (None at root)
  • children   – list of child GameTreeNode objects (populated lazily by expand())
  • value      – the backed-up Minimax value (set during search)

The tree is generated DYNAMICALLY during search (not pre-built), which is the
standard approach for depth-limited forward search. The expand() method creates
the immediate children by applying all legal moves to the current state.

Academic note:
    Storing explicit nodes (rather than just recursing with state) allows us to:
      1. Count nodes_generated and nodes_evaluated for the statistics module.
      2. Reconstruct the best move path after search.
      3. Provide a visual representation of the search tree for debugging.
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

from game.state import GameState
from game.rules import get_legal_moves, apply_move

if TYPE_CHECKING:
    from experiments.runner import MoveStats


class GameTreeNode:
    """
    A single node in the game search tree.

    Attributes
    ----------
    state : GameState
        The game state represented by this node.
    move : str or None
        The move ("LEFT" or "RIGHT") that was applied to reach this node.
        None for the root node.
    parent : GameTreeNode or None
        Parent node; None for the root.
    children : list[GameTreeNode]
        Child nodes (created by expand()).
    value : float or None
        The backed-up Minimax/Alpha-Beta value assigned during search.
        None until the search algorithm sets it.
    depth : int
        Depth of this node from the root (root = 0).
    """

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

    # ── Tree expansion ─────────────────────────────────────────────────────────

    def expand(self, nodes_generated_counter: Optional[list] = None) -> List["GameTreeNode"]:
        """
        Generate and store all child nodes for this node.

        Children are created for every legal move in the current state.
        Each child's depth is this node's depth + 1.

        Parameters
        ----------
        nodes_generated_counter : list, optional
            A single-element list [count] used as a mutable counter so the
            caller (Minimax / Alpha-Beta) can track total nodes generated.
            Passed by reference to avoid global state.

        Returns
        -------
        list[GameTreeNode]
            The newly created child nodes (also stored in self.children).
        """
        if self.children:
            # Already expanded — return cached children
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

            # Increment the external counter if provided
            if nodes_generated_counter is not None:
                nodes_generated_counter[0] += 1

        return self.children

    # ── Convenience ───────────────────────────────────────────────────────────

    def is_terminal(self) -> bool:
        """True if this node represents a completed game (empty sequence)."""
        from game.rules import is_terminal
        return is_terminal(self.state)

    def best_child(self, maximizing: bool) -> Optional["GameTreeNode"]:
        """
        Return the child with the highest (maximizing) or lowest (minimizing)
        value. Useful for reconstructing the best move after search.

        Assumes all children have been evaluated (value is not None).
        """
        if not self.children:
            return None
        key = (lambda c: c.value) if c.value is not None else (lambda _: 0)
        if maximizing:
            return max(self.children, key=lambda c: c.value if c.value is not None else float('-inf'))
        else:
            return min(self.children, key=lambda c: c.value if c.value is not None else float('inf'))

    def __repr__(self) -> str:
        return (
            f"GameTreeNode(move={self.move!r}, depth={self.depth}, "
            f"value={self.value}, state={self.state})"
        )
