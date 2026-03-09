# Number Sequence Game — Project Documentation

> **Course:** Artificial Intelligence (RTU MAP)
> **Language:** Python 3.9+
> **Dependencies:** Standard library only (`tkinter`, `json`, `csv`, `time`, `random`)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Game Rules](#2-game-rules)
3. [Project Architecture](#3-project-architecture)
4. [How to Run](#4-how-to-run)
5. [Using the GUI](#5-using-the-gui)
   - 5.1 [Setup Screen — Game Tab](#51-setup-screen--game-tab)
   - 5.2 [Playing the Game](#52-playing-the-game)
   - 5.3 [Batch Experiment Tab](#53-batch-experiment-tab)
6. [Core Data Structures](#6-core-data-structures)
   - 6.1 [GameState](#61-gamestate)
   - 6.2 [GameTreeNode](#62-gametreenode)
7. [AI Algorithms](#7-ai-algorithms)
   - 7.1 [Minimax](#71-minimax)
   - 7.2 [Alpha-Beta Pruning](#72-alpha-beta-pruning)
   - 7.3 [Heuristic Evaluation Function](#73-heuristic-evaluation-function)
   - 7.4 [Comparison: Minimax vs Alpha-Beta](#74-comparison-minimax-vs-alpha-beta)
8. [Statistics: nodes_generated and nodes_evaluated](#8-statistics-nodes_generated-and-nodes_evaluated)
9. [Experiments & Logging](#9-experiments--logging)
   - 9.1 [BatchRunner](#91-batchrunner)
   - 9.2 [CSV Export](#92-csv-export)
   - 9.3 [JSON Export](#93-json-export)
10. [File-by-File Reference](#10-file-by-file-reference)
11. [Academic Defense Notes](#11-academic-defense-notes)

---

## 1. Project Overview

This project implements a **deterministic, two-player, perfect-information combinatorial game** as required by the RTU AI course practical assignment. The program includes:

- A well-defined game with branching factor **2** at every non-terminal state
- **Depth-limited Minimax** — the reference adversarial search algorithm
- **Depth-limited Alpha-Beta Pruning** — an optimised Minimax that prunes provably irrelevant branches
- An **explicit game tree** (`GameTreeNode`) built dynamically during search
- A **heuristic evaluation function** used when the depth limit is reached
- A **Tkinter GUI** for playing Human vs AI or AI vs AI
- A **batch experiment runner** that plays K automated games and computes aggregate statistics
- **CSV and JSON export** of full game logs for analysis

---

## 2. Game Rules

### Setup

| Parameter | Value |
|-----------|-------|
| Sequence length N | User selects **15 – 25** |
| Sequence values | Each element is **1, 2, or 3** (random) |
| Both players start with | **80 points** each |

### Gameplay

1. The program generates a random sequence of N numbers, e.g. `[2, 1, 3, 2, 1, 3, ...]`
2. Players alternate turns.
3. On each turn, the current player **must take either the leftmost or the rightmost** number from the sequence.
4. The taken number is **subtracted from that player's own points**.
5. The game ends when the sequence is **empty** (all N numbers have been taken).

### Winning Condition

| Condition | Result |
|-----------|--------|
| P1 points > P2 points | **Player 1 wins** |
| P2 points > P1 points | **Player 2 wins** |
| Equal points | **Draw** |

> **Strategic insight:** Each player wants to take *small* numbers (subtracting less from their own points) and force the opponent to take *large* numbers. This is why the LEFT/RIGHT choice creates genuine strategic depth — taking a small number on the left might expose a large number on the right for the opponent, and vice versa.

### Why LEFT or RIGHT only?

This is the classical *Optimal Game Strategy* problem from competitive programming and game theory (Cormen et al., Introduction to Algorithms, exercise 15.8). It gives:
- **Branching factor = 2** at every state (except possibly the last move — when 1 element remains, both LEFT and RIGHT refer to the same element, so only 1 move is generated).
- A tree that is tractable for Minimax with reasonable depth limits.
- Full information for both players at all times.

---

## 3. Project Architecture

```
MAP_first_practical/
│
├── main.py                  ← Entry point (run this)
│
├── game/
│   ├── state.py             ← GameState dataclass (immutable)
│   ├── rules.py             ← get_legal_moves, apply_move, is_terminal, get_winner, generate_sequence
│   └── node.py              ← GameTreeNode (explicit tree structure for search)
│
├── ai/
│   ├── minimax.py           ← Depth-limited Minimax
│   ├── alphabeta.py         ← Depth-limited Alpha-Beta Pruning
│   └── heuristic.py         ← Heuristic evaluation + terminal scoring
│
├── experiments/
│   ├── runner.py            ← BatchRunner, MoveStats, MoveRecord, GameRecord, PlayerConfig
│   └── logger.py            ← GameLogger (CSV + JSON export)
│
├── gui/
│   ├── app.py               ← Root Tk window + tab switching
│   ├── setup_frame.py       ← Game configuration screen
│   ├── game_frame.py        ← Live game view
│   └── experiment_frame.py  ← Batch experiment panel
│
└── results/                 ← Default save location for exports
```

### Dependency Flow

```
main.py
  └── gui/app.py
        ├── gui/setup_frame.py  →  game/rules.py, game/state.py
        ├── gui/game_frame.py   →  game/rules.py, game/state.py
        │                           ai/minimax.py, ai/alphabeta.py
        │                           experiments/runner.py (MoveRecord, GameRecord)
        └── gui/experiment_frame.py → experiments/runner.py (BatchRunner)
                                       experiments/logger.py (GameLogger)

ai/minimax.py      →  game/node.py, game/rules.py, ai/heuristic.py
ai/alphabeta.py    →  game/node.py, game/rules.py, ai/heuristic.py
experiments/runner.py → game/state.py, game/rules.py, ai/minimax.py, ai/alphabeta.py
```

---

## 4. How to Run

### Requirements

- **Python 3.9 or later** — check with `python --version`
- **No external packages** — only Python standard library is used

### Starting the Application

```powershell
# Navigate to the project root
cd C:\Users\georg\Programming\MAP_first_practical

# Run the application
python main.py
```

The Tkinter window will open immediately with two tabs: **Game** and **Experiments**.

---

## 5. Using the GUI

### 5.1 Setup Screen — Game Tab

When the application opens you see the **Setup Screen**:

#### Step 1 — Choose Game Mode

| Mode | Description |
|------|-------------|
| **Human vs AI** | You play against one of the AI algorithms |
| **AI vs AI** | Two AI algorithms play each other automatically |

#### Step 2 — Configure the Sequence

1. Set **N** (sequence length) between 15 and 25 using the spinner.
2. Click **🎲 Generate Sequence** — a random sequence is created and displayed.
   - You must generate a sequence before starting.

#### Step 3 — Configure Players

**Human vs AI mode:**
- Player 1 is always *you* (Human).
- Player 2: select the AI algorithm (**Minimax** or **Alpha-Beta**) and **depth** (1–12).
- Choose **Who Goes First**: Human first or AI first.

**AI vs AI mode:**
- Configure algorithm and depth for **both** Player 1 and Player 2 independently.
- Player 1 always goes first in AI vs AI mode.

#### Step 4 — Start the Game

Click **▶ Start Game**. The game screen appears.

---

### 5.2 Playing the Game

The game screen shows:

- **Scoreboard** — both players' current points and whose turn it is.
- **Sequence display** — all remaining numbers; the two ends are highlighted in colour.
- **Move buttons** (Human vs AI only):
  - **◀ Take LEFT** — take the leftmost number.
  - **Take RIGHT ▶** — take the rightmost number.
- **Move History log** — every move is recorded with player, direction, value taken, and AI statistics.

#### Human Turn

The LEFT and RIGHT buttons become active when it is your turn. Click one to make your move. The button taken animates briefly, then the AI calculates its response.

#### AI Turn

Buttons are disabled while the AI is thinking. A status bar shows `"AI (minimax, depth=5) is thinking…"`. After the AI finishes (typically < 1 second for depth ≤ 8 on sequences of length ≤ 25), its move is applied and the log entry is added with:
- The move direction and value taken
- `gen=` nodes generated (how many tree nodes were created)
- `eval=` nodes evaluated (how many leaf nodes were scored with the heuristic or terminal function)
- Time in milliseconds

#### Game End

When the sequence is empty, the result banner appears in the status bar and a summary is logged at the bottom of the Move History.

Click **← Back** to return to the Setup screen and start a new game.

---

### 5.3 Batch Experiment Tab

The **Experiments** tab allows you to run K automated games between two AI algorithms and collect aggregate statistics.

#### Configuration

| Field | Description |
|-------|-------------|
| **Games (K)** | Number of games to run (1–1000) |
| **Seq length (N)** | Sequence length for each game (15–25) |
| **Seed** | Random seed for reproducibility (leave blank for random) |
| **Player 1 / Player 2** | Algorithm (Minimax or Alpha-Beta) and depth per player |

> **Note:** Starting player alternates each game (P1 first in even games, P2 first in odd games) for statistical fairness.

#### Running

Click **▶ Run Experiments**. A background thread runs all games without blocking the GUI. A progress counter updates during execution.

#### Results

After completion, the results panel shows:

```
──────────────────────────────────────────────────
  Batch Results  (10 games)
──────────────────────────────────────────────────
  Player 1 (Minimax(P1, d=5)):  4 wins
  Player 2 (Alphabeta(P2, d=5)):  5 wins
  Draws:               1
──────────────────────────────────────────────────
  P1 nodes generated:  18432
  P1 nodes evaluated:  9216
  P1 avg time/move:    2.341 ms
  P2 nodes generated:  9814    ← fewer because of pruning!
  P2 nodes evaluated:  5120
  P2 avg time/move:    1.287 ms
──────────────────────────────────────────────────
```

#### Exporting

- **💾 Export CSV** — one row per game (summary statistics)
- **💾 Export JSON** — full detail including every individual move

---

## 6. Core Data Structures

### 6.1 GameState

**File:** `game/state.py`

`GameState` is a **frozen (immutable) dataclass** — it cannot be modified after creation. This is critical for correctness: each move creates a *new* state rather than mutating the current one.

```python
@dataclass(frozen=True)
class GameState:
    sequence:  Tuple[int, ...]   # Remaining numbers; index 0 = leftmost
    p1_points: int               # Player 1 remaining points
    p2_points: int               # Player 2 remaining points
    turn:      int               # 1 = Player 1's turn, 2 = Player 2's turn
```

**Key properties:**

| Property | Description |
|----------|-------------|
| `current_player_points` | Points of the player who is about to move |
| `opponent_points` | Points of the player who is waiting |
| `points_of(player_id)` | Points for a specific player ID |

**Initial state:** Both players start at **80 points**. Created by `make_initial_state(sequence, first_player)`.

---

### 6.2 GameTreeNode

**File:** `game/node.py`

The explicit **node in the Minimax/Alpha-Beta search tree**. Storing nodes explicitly (rather than just recursing with states) allows counting nodes generated/evaluated and reconstructing the best path.

```python
class GameTreeNode:
    state:    GameState          # The game state at this node
    move:     str | None        # Move that led to this node ("LEFT"/"RIGHT"); None at root
    parent:   GameTreeNode | None
    children: List[GameTreeNode] # Populated lazily by expand()
    value:    float | None      # Minimax value (set during search)
    depth:    int               # Distance from root (root = 0)
```

#### `expand(stats=None)` Method

Creates all child nodes by applying every legal move to the current state.

```
Root node (depth 0)
  ├── LEFT child  (depth 1)  — took left element
  └── RIGHT child (depth 1)  — took right element
       ├── LEFT child  (depth 2)
       └── RIGHT child (depth 2)
            └── ...
```

Each created child node increments `stats.nodes_generated` by 1, giving an accurate per-node count.

---

## 7. AI Algorithms

### 7.1 Minimax

**File:** `ai/minimax.py`

Minimax is the foundational adversarial search algorithm for two-player zero-sum games.

#### Core Idea

```
My turn (MAXIMIZER):  pick the move that gives the HIGHEST value
Opponent's turn (MINIMIZER): pick the move that gives the LOWEST value
```

Both players are assumed to play **perfectly optimally**.

#### Pseudocode

```
function minimax(node, depth, maximizing, player_id):
    if terminal(node.state):
        return terminal_score(winner, player_id)   # +∞ win, -∞ loss, 0 draw
    if depth == 0:
        return heuristic(node.state, player_id)    # depth limit reached

    node.expand()   # Create all children

    if maximizing:
        best = -∞
        for each child:
            val = minimax(child, depth-1, FALSE, player_id)
            best = max(best, val)
        return best
    else:
        best = +∞
        for each child:
            val = minimax(child, depth-1, TRUE, player_id)
            best = min(best, val)
        return best
```

#### Entry Point

```python
move, value, stats = get_best_move_minimax(state, depth=5, player_id=1)
```

Returns:
- `move` — `"LEFT"` or `"RIGHT"` (best move)
- `value` — the Minimax value of the chosen move
- `stats` — `MoveStats` object with `nodes_generated`, `nodes_evaluated`, `time_s`

#### Complexity

| Metric | Value |
|--------|-------|
| Time | O(b^d) where b=2 (branching factor), d=depth |
| Space | O(b × d) for the call stack |
| Depth 5, N=20 | ≈ 2^5 = 32 leaf evaluations per move (minimal) |
| Depth 10, N=20 | ≈ 2^10 = 1024 leaf evaluations per move |

---

### 7.2 Alpha-Beta Pruning

**File:** `ai/alphabeta.py`

Alpha-Beta Pruning is **Minimax with a pruning optimisation**. It maintains two bounds:

| Bound | Meaning |
|-------|---------|
| **α (alpha)** | Best value the **maximizer** can guarantee so far on the current path |
| **β (beta)**  | Best value the **minimizer** can guarantee so far on the current path |

#### Pruning Conditions

```
β ≤ α  →  prune (stop exploring this branch)
```

- **β-cutoff** (in a maximizing node): The minimizer already has a move that gives a value ≤ α. The maximizer won't be allowed to reach this branch anyway.
- **α-cutoff** (in a minimizing node): The maximizer already found a better option elsewhere.

#### Pseudocode

```
function alphabeta(node, depth, α, β, maximizing, player_id):
    if terminal(node.state):
        return terminal_score(...)
    if depth == 0:
        return heuristic(...)

    node.expand()

    if maximizing:
        value = -∞
        for each child:
            value = max(value, alphabeta(child, depth-1, α, β, FALSE, player_id))
            α = max(α, value)
            if β ≤ α: break    ← β-cutoff: prune remaining children
        return value
    else:
        value = +∞
        for each child:
            value = min(value, alphabeta(child, depth-1, α, β, TRUE, player_id))
            β = min(β, value)
            if β ≤ α: break    ← α-cutoff: prune remaining children
        return value
```

#### Key Property

> **Alpha-Beta always produces the same answer as Minimax.** It is purely an efficiency optimisation — it prunes branches that cannot possibly affect the final decision.

#### Efficiency Gains

| Move Ordering | Effective Branching Factor | Depth Gain |
|---------------|---------------------------|------------|
| Worst case (no pruning) | b = 2 | Same as Minimax |
| Average case (random order) | b^(3/4) ≈ 1.68 | ~33% more depth |
| Best case (perfect ordering) | √b ≈ 1.41 | **Doubles** the effective depth |

Since this game has no move ordering (LEFT before RIGHT always), the actual gain is close to the average case.

---

### 7.3 Heuristic Evaluation Function

**File:** `ai/heuristic.py`

Used when the search hits the depth limit on a **non-terminal state**. The function must be fast and should correlate with the true game outcome.

#### Design

```
H(state, player_id) = PRIMARY_TERM + SECONDARY_TERM
```

**Primary term — point difference:**
```
PRIMARY = my_points − opponent_points
```
If I have more points than my opponent, the position is good for me. This is a directly interpretable, defensible metric.

**Secondary term — look-ahead end-value bias:**
```
SECONDARY = −0.1 × max(leftmost_element, rightmost_element)
           (applied only when it is our turn next)
```
If large numbers (2 or 3) sit at the ends of the sequence and it is our turn, we must take one of them on our next move, costing us more points. The coefficient `0.1` keeps this term minor (max penalty = 0.3) so it does not dominate the primary term.

#### Terminal Scoring

For terminal states (sequence empty), exact scores are used instead of the heuristic:

| Outcome | Score |
|---------|-------|
| Win | +1,000,000 |
| Loss | −1,000,000 |
| Draw | 0 |

Large sentinel values ensure that any winning position is preferred over any non-terminal heuristic value, regardless of the point difference.

---

### 7.4 Comparison: Minimax vs Alpha-Beta

| Feature | Minimax | Alpha-Beta |
|---------|---------|-----------|
| Result quality | Optimal | Identical to Minimax |
| Nodes generated | All branches at each depth | Fewer — pruned branches omitted |
| Speed | Slower | Faster (≈ 2× average improvement) |
| Implementation complexity | Simpler | Slightly more complex (α/β params) |
| nodes_generated metric | Higher | **Lower** (this is the visible proof of pruning) |
| Use case | Academic reference | Practical/competitive |

---

## 8. Statistics: nodes_generated and nodes_evaluated

These two metrics are collected in a `MoveStats` object per AI call:

| Metric | Definition |
|--------|-----------|
| **nodes_generated** | Number of `GameTreeNode` objects created during search (incremented in `expand()` per child) |
| **nodes_evaluated** | Number of *leaf* nodes that were scored — either by the heuristic (depth limit) or terminal function |

### Why they differ

- Every expanded node generates children → `nodes_generated`
- Only leaf nodes (terminal or at depth limit) are evaluated → `nodes_evaluated`
- Interior nodes are neither evaluated nor counted in `nodes_evaluated`

### Example (depth=2, sequence length 5)

```
Root (not evaluated)
├── LEFT child (expanded)
│    ├── LL leaf  (evaluated) ✓
│    └── LR leaf  (evaluated) ✓
└── RIGHT child (expanded)
     ├── RL leaf  (evaluated) ✓
     └── RR leaf  (evaluated) ✓

nodes_generated = 4   (2 at depth 1 + 2 at depth 2)
nodes_evaluated = 4   (all depth-2 leaves)
```

For Alpha-Beta, if the RR branch is pruned:
```
nodes_generated = 3   (RL not created → fewer generated)
nodes_evaluated = 3
```

---

## 9. Experiments & Logging

### 9.1 BatchRunner

**File:** `experiments/runner.py`

```python
runner = BatchRunner()
records, stats = runner.run(
    K=10,           # number of games
    n=20,           # sequence length
    p1_config=PlayerConfig(player_id=1, kind="minimax",   depth=5),
    p2_config=PlayerConfig(player_id=2, kind="alphabeta", depth=5),
    seed=42,        # optional; None = random
)
```

**What it does:**
1. Generates a new random sequence for each game (using the seeded RNG for reproducibility).
2. Alternates the starting player (P1 first in game 0, P2 first in game 1, etc.) for fairness.
3. Runs each game to completion, recording every move.
4. Accumulates aggregate `BatchStats` (wins, draws, total nodes, avg time per move).

**Data classes:**

| Class | Purpose |
|-------|---------|
| `MoveStats` | Per-move AI statistics (nodes_generated, nodes_evaluated, time_s) |
| `MoveRecord` | Full record of one move (player, direction, value taken, points after, AI stats) |
| `GameRecord` | Full record of one game (initial sequence, all moves, winner, final points) |
| `PlayerConfig` | `player_id`, `kind` ("minimax"/"alphabeta"), `depth` |
| `BatchStats` | K-game aggregate: wins/draws/losses per player, summed node counts |

---

### 9.2 CSV Export

One row per game — useful for importing into Excel or pandas for analysis.

**Columns:**

| Column | Description |
|--------|-------------|
| `game_id` | 0-indexed game number |
| `initial_sequence` | The sequence as a Python list string |
| `starting_player` | 1 or 2 |
| `p1_algo`, `p1_depth` | Player 1 config |
| `p2_algo`, `p2_depth` | Player 2 config |
| `winner` | 0=draw, 1=P1, 2=P2 |
| `final_p1_points`, `final_p2_points` | Points at game end |
| `total_moves` | N (all elements taken) |
| `total_time_s` | Wall-clock seconds for the whole game |
| `p1_nodes_generated`, `p1_nodes_evaluated`, `p1_total_time_s` | P1 AI totals |
| `p2_nodes_generated`, `p2_nodes_evaluated`, `p2_total_time_s` | P2 AI totals |

---

### 9.3 JSON Export

Full detail — one object per game, including the complete move-by-move history.

```json
[
  {
    "game_id": 0,
    "initial_sequence": [2, 1, 3, ...],
    "starting_player": 1,
    "p1_config": {"player_id": 1, "kind": "minimax", "depth": 5},
    "p2_config": {"player_id": 2, "kind": "alphabeta", "depth": 5},
    "winner": 2,
    "final_p1_points": 68,
    "final_p2_points": 71,
    "total_time_s": 0.234,
    "moves": [
      {
        "move_index": 0,
        "player_turn": 1,
        "action": "LEFT",
        "value_taken": 2,
        "p1_points_after": 78,
        "p2_points_after": 80,
        "sequence_after": [1, 3, ...],
        "time_s": 0.003,
        "nodes_generated": 62,
        "nodes_evaluated": 32,
        "algorithm": "minimax"
      },
      ...
    ]
  }
]
```

---

## 10. File-by-File Reference

| File | Key Exports | Description |
|------|------------|-------------|
| `main.py` | — | Entry point; launches the Tkinter `App` |
| `game/state.py` | `GameState`, `make_initial_state`, `INITIAL_POINTS`, `MIN_N`, `MAX_N` | Immutable game state dataclass |
| `game/rules.py` | `get_legal_moves`, `apply_move`, `is_terminal`, `get_winner`, `generate_sequence` | All game logic |
| `game/node.py` | `GameTreeNode` | Explicit tree node with lazy `expand()` |
| `ai/minimax.py` | `get_best_move_minimax`, `minimax` | Depth-limited Minimax |
| `ai/alphabeta.py` | `get_best_move_alphabeta`, `alphabeta` | Depth-limited Alpha-Beta |
| `ai/heuristic.py` | `evaluate`, `terminal_score` | Heuristic evaluation and terminal scoring |
| `experiments/runner.py` | `BatchRunner`, `PlayerConfig`, `MoveStats`, `MoveRecord`, `GameRecord`, `BatchStats` | Automated game runner + statistics |
| `experiments/logger.py` | `GameLogger.export_csv`, `GameLogger.export_json` | CSV and JSON serialisation |
| `gui/app.py` | `App` | Root window, tab switching (Game / Experiments) |
| `gui/setup_frame.py` | `SetupFrame` | Configuration screen |
| `gui/game_frame.py` | `GameFrame` | Live game view with move buttons and log |
| `gui/experiment_frame.py` | `ExperimentFrame` | Batch experiment panel with export |

---

## 11. Academic Defense Notes

### Why LEFT/RIGHT (not any position)?

Taking from ends only gives **branching factor 2**, making trees tractable. Taking from any position gives branching factor N (up to 25), which makes depth-5 Minimax explore 25^5 = ~9.7 million nodes per move — impractical. Taking only the first element gives branching factor 1, making the "game" trivial with no decision to make.

### Why immutable GameState?

Immutable states prevent aliasing bugs. When the search creates a child state via `apply_move`, the parent state is guaranteed unchanged. This is essential for correct backtracking in Minimax.

### Why explicit GameTreeNode instead of pure recursion?

Pure recursion does not store the tree structure, so it cannot:
- Count `nodes_generated` accurately
- Reconstruct the best path after search
- Be visualised or debugged

### Why 80 initial points?

With N=25 numbers from {1,2,3} and mean value 2, the total sum of numbers is ≈ 50. Each player takes ≈ 25 numbers on average. With initial points 80, final points are typically in the range 55–75, large enough for meaningful differences while keeping the game short and tractable.

### Alpha-Beta correctness

Alpha-Beta always returns the **same move and value** as Minimax for the same depth. The only difference is `nodes_generated` and `nodes_evaluated`. If your experiments show different win rates for Minimax vs Alpha-Beta at the same depth, it indicates a bug in the implementation — they must agree.

### Heuristic admissibility

The heuristic is not admissible in the formal sense (this game is not a pathfinding problem). However, it is:
- **Monotone with outcome**: more point difference → higher score
- **Bounded**: never exceeds ±1,000,000 (reserved for terminal states)
- **Fast**: O(1) computation (no recursion)
- **Explainable**: both terms have clear intuitive justification

### Depth limit effect

| Depth | Tree nodes explored (approx.) | Typical time per move |
|-------|-------------------------------|----------------------|
| 3 | 8 | < 1 ms |
| 5 | 32 | < 5 ms |
| 7 | 128 | < 20 ms |
| 10 | 1,024 | < 100 ms |
| 15 | 32,768 | 1–3 s |

Higher depth → stronger play but longer calculation time. Depth 5–7 is the recommended balance for smooth Human vs AI gameplay.

---

## 12. Alpha-Beta Step-by-Step Example (Human vs AI, Depth 4)

This section gives a **concrete, line-by-line mental model** of how the implemented code behaves when a **human plays against the Alpha-Beta AI** on a **fixed sequence**:

- Sequence: `[1, 3, 2, 1, 3, 1, 1, 2]`
- Initial points: `P1 = 80`, `P2 = 80`
- Game mode: **Human vs AI**
- Player 1: **Human**
- Player 2: **AI (Alpha-Beta)**
- Search depth for AI: **4**
- Starting player: **Player 1 (Human)** moves first

We will walk through:

1. How the **game state** is represented (`GameState`).
2. How **human moves** change the state.
3. How, on AI turns, `GameFrame` calls `get_best_move_alphabeta`.
4. How `GameTreeNode.expand` builds the local search tree.
5. How `alphabeta` recursively explores the tree with **α/β pruning**.
6. How the chosen move is applied back into the live game state.

### 12.1 Initial GameState

When the game starts on this fixed sequence in Human vs AI mode, the GUI creates the initial state:

```python
from game.state import make_initial_state

sequence = (1, 3, 2, 1, 3, 1, 1, 2)
state0 = make_initial_state(sequence, first_player=1)
```

This produces:

- `state0.sequence  = (1, 3, 2, 1, 3, 1, 1, 2)`
- `state0.p1_points = 80`
- `state0.p2_points = 80`
- `state0.turn      = 1`  (it is Player 1's turn)

In the GUI (`GameFrame`), this state is stored as:

- `self._state = state0`

The sequence is rendered visually, and the status line shows:  
**"Turn: P1"**, with the **LEFT/RIGHT buttons enabled** for the human.

### 12.2 Turn 1 — Human Move

Suppose the human (Player 1) chooses to take **LEFT** on the first move.

#### 12.2.1 How the GUI applies the human move

In `gui/game_frame.py`, the human button calls:

```python
self._human_move(MOVE_LEFT)
```

Inside `_human_move`:

1. It records which player is moving: `player = self._state.turn` (this is P1).
2. It calls `_apply_and_record(move, algo="human", ...)`.

```python
new_state = apply_move(self._state, move)
self._state = new_state
```

The `apply_move` function in `game/rules.py` performs the actual state transition:

- Sequence before: `(1, 3, 2, 1, 3, 1, 1, 2)`
- Move: `"LEFT"` → take the leftmost element `1`
- Current player: `turn = 1` (Player 1)

Result:

- New sequence: `(3, 2, 1, 3, 1, 1, 2)`
- New points:
  - `p1_points = 80 - 1 = 79`
  - `p2_points = 80`
- Next turn: `turn = 2` (it becomes Player 2's turn)

So after the human move:

- `state1.sequence  = (3, 2, 1, 3, 1, 1, 2)`
- `state1.p1_points = 79`
- `state1.p2_points = 80`
- `state1.turn      = 2`

The GUI updates `self._state = state1`, redraws the board, logs the move, and then calls:

```python
self._advance_game()
```

### 12.3 Turn 2 — AI (Alpha-Beta) Takes Over

Inside `_advance_game`, the code checks whose turn it is:

- `current = self._state.turn  # = 2`
- It selects Player 2's config: `cfg = self._p2_config`
- Because `cfg.kind == "alphabeta"`, it knows this is an **AI turn**.

The GUI:

- Disables the human buttons,
- Shows the status: _"AI (alphabeta, depth=4) is thinking…"_,
- Schedules a call to `_ai_move` after a short delay (`self.after(80, self._ai_move)`).

When `_ai_move` runs, for Player 2:

```python
from ai.alphabeta import get_best_move_alphabeta
move, _, stats = get_best_move_alphabeta(self._state, cfg.depth, current)
```

At this moment:

- `state = state1`
- `depth = 4`
- `player_id = 2` (the AI player)

### 12.4 `get_best_move_alphabeta`: Root Node and Children

Inside `ai/alphabeta.py`, the entry function does:

1. Asserts that `state.turn == player_id == 2`.
2. Creates the **root node**:

   ```python
   root = GameTreeNode(state=state1, move=None, parent=None, depth=0)
   stats = MoveStats()
   ```

3. Expands the root once:

   ```python
   root.expand(nodes_generated_counter=None)
   stats.nodes_generated += len(root.children)
   ```

At this point, `root.state` is:

- `(3, 2, 1, 3, 1, 1, 2)`, `p1=79`, `p2=80`, `turn=2`.

#### 12.4.1 Children of the root

Legal moves: `"LEFT"` and `"RIGHT"` (sequence is non-empty).

- **Child A (AI plays LEFT)**:
  - Takes `3` from the left.
  - New sequence: `(2, 1, 3, 1, 1, 2)`
  - New points: `p2_points = 80 - 3 = 77`, `p1_points = 79`
  - Next turn: `turn = 1` (Player 1)
  - This is stored as:
    - `child_A = GameTreeNode(state=state_A, move="LEFT", parent=root, depth=1)`

- **Child B (AI plays RIGHT)**:
  - Takes `2` from the right.
  - New sequence: `(3, 2, 1, 3, 1, 1)`
  - New points: `p2_points = 80 - 2 = 78`, `p1_points = 79`
  - Next turn: `turn = 1`
  - Stored as:
    - `child_B = GameTreeNode(state=state_B, move="RIGHT", parent=root, depth=1)`

So the **local search tree root** for this AI move has two branches:

```
Root (P2 to move)
 ├── LEFT  → child_A  (P1 to move)
 └── RIGHT → child_B  (P1 to move)
```

### 12.5 `alphabeta` Recursion (Depth 4)

`get_best_move_alphabeta` then calls `alphabeta` on each child of the root:

```python
best_move  = None
best_value = -inf
alpha = -inf
beta  = +inf

for child in root.children:
    child_value = alphabeta(
        child,
        depth - 1,   # 3 remaining plies below this child
        alpha,
        beta,
        maximizing=False,  # after AI's move, it is the human's turn → MINIMIZER
        player_id=2,
        stats=stats,
    )
    ...
```

Because we started with `depth = 4` at the root, each child is explored with:

- `depth = 3`
- `maximizing = False` (it becomes the **human's turn**, who is the **minimizer** from the AI's perspective).

We will trace the **LEFT child (child_A)** in detail; the RIGHT child behaves symmetrically with different numbers.

#### 12.5.1 Node A (human to move) — level 1

At node A:

- `state_A.sequence  = (2, 1, 3, 1, 1, 2)`
- `state_A.p1_points = 79`
- `state_A.p2_points = 77`
- `state_A.turn      = 1` (Human)
- `depth = 3`
- `maximizing = False`

The `alphabeta` function checks:

1. `is_terminal(state_A)`? → **No**, sequence is non-empty.
2. `depth == 0`? → **No**, depth is 3.
3. Calls `node.expand()`:

   - Human can again choose `"LEFT"` or `"RIGHT"`.
   - Each move applies `apply_move` to `state_A` and creates child nodes.

So we get two grandchildren from A:

- **A1 (human LEFT)**:
  - Takes `2` from the left.
  - New sequence: `(1, 3, 1, 1, 2)`
  - `p1_points = 79 - 2 = 77`, `p2_points = 77`
  - Next `turn = 2` (AI)

- **A2 (human RIGHT)**:
  - Takes `2` from the right.
  - New sequence: `(2, 1, 3, 1, 1)`
  - `p1_points = 79 - 2 = 77`, `p2_points = 77`
  - Next `turn = 2`

At node A (minimizer):

```python
value = +inf
for each child in [A1, A2]:
    child_value = alphabeta(child, depth=2, alpha, beta, maximizing=True, ...)
    value = min(value, child_value)
    beta  = min(beta, value)
    if beta <= alpha:
        break   # α-cutoff (if it happens)
```

Both A1 and A2 will be explored (unless a cutoff happens early) as **maximizing nodes** because the turn switches back to the AI.

#### 12.5.2 Node A1 (AI to move) — level 2

Node A1:

- `turn = 2` (AI), so `maximizing = True` in recursive call.
- `depth = 2`.

Again:

1. Not terminal, depth not zero.
2. `expand()` generates **two more children** (A1L, A1R) corresponding to AI choosing LEFT or RIGHT.
3. For each of these, `alphabeta` is called with:
   - `depth = 1`
   - `maximizing = False` (back to the human).

This process repeats until we reach:

- Either a **terminal state** (`sequence` empty), or
- The **depth limit** (`depth == 0`).

At **depth 0**, the function does **not expand** further. Instead, it uses the heuristic:

```python
value = evaluate(state, player_id=2)  # perspective of AI player (P2)
```

This heuristic:

- Computes `AI_points - Human_points`,
- Optionally subtracts a small penalty based on the larger of the two ends if it is AI's turn,
- Returns a **float** representing how good this leaf is for P2.

#### 12.5.3 Propagating values and pruning

On the way back up:

- At **leaf nodes**, `alphabeta` returns the heuristic value.
- At **maximizing nodes** (AI turn):

  ```python
  value = max(value, child_value)
  alpha = max(alpha, value)
  if beta <= alpha:
      break   # β-cutoff
  ```

  If the AI already found a child with value ≥ current `beta`, there is no need to explore further children — the minimizer above will avoid this branch anyway.

- At **minimizing nodes** (human turn):

  ```python
  value = min(value, child_value)
  beta  = min(beta, value)
  if beta <= alpha:
      break   # α-cutoff
  ```

  If the human (minimizer) has a move that ensures a value ≤ current `alpha`, further children of this node cannot improve the AI's position and are pruned.

Thus, for node A, `alphabeta` returns a single backed-up score like:

- `value_A = some_float` (e.g., `-0.3` or `1.2`), representing the **best guaranteed outcome for P2** if P2 plays LEFT at the root and both sides are optimal within depth 4.

The same happens for node B (the RIGHT move at the root), yielding `value_B`.

### 12.6 Choosing the Best Move at the Root

Back in `get_best_move_alphabeta`, after both children have been evaluated (with possible pruning inside each subtree):

```python
for child in root.children:
    child_value = alphabeta(...)
    if child_value > best_value:
        best_value = child_value
        best_move  = child.move
    alpha = max(alpha, best_value)
```

So:

- If `value_A > value_B`, then:
  - `best_move = "LEFT"`
  - `best_value = value_A`
- Otherwise, `best_move = "RIGHT"`.

The function returns:

```python
return best_move, best_value, stats
```

Where:

- `best_move` is the chosen `"LEFT"` or `"RIGHT"` for this AI turn,
- `best_value` is the Alpha-Beta score of that move,
- `stats` contains:
  - `nodes_generated` — how many `GameTreeNode` objects were created,
  - `nodes_evaluated` — how many leaf nodes were scored,
  - `time_s` — total time spent.

### 12.7 Applying the AI Move Back Into the Live Game

Returning to `GameFrame._ai_move`:

```python
move, _, stats = get_best_move_alphabeta(self._state, cfg.depth, current)

self._apply_and_record(
    move,
    algo=cfg.kind,  # "alphabeta"
    nodes_gen=stats.nodes_generated,
    nodes_eval=stats.nodes_evaluated,
    t=elapsed,
)
```

Here:

1. `_apply_and_record` calls `apply_move(self._state, move)` again, exactly as for human moves, producing a new `GameState` (now it will be the human's turn again).
2. The move is recorded into a `MoveRecord` with:
   - Which player moved,
   - Direction (`LEFT`/`RIGHT`),
   - Value taken,
   - Points after the move,
   - `nodes_generated`, `nodes_evaluated`, and time.
3. The GUI is refreshed: updated sequence, updated points, and `"Turn: P1"` for the human.
4. Then `_advance_game` runs again, and the loop continues: human moves (no search), then AI moves (Alpha-Beta with depth 4 from the new state), until the sequence is empty.

### 12.8 Summary of the "Under the Hood" Flow

For **each AI turn** in this example game:

1. The current `GameState` (e.g., after human moves on `[1, 3, 2, 1, 3, 1, 1, 2]`) is passed to `get_best_move_alphabeta`.
2. A **local game tree** of depth at most 4 is built dynamically from that state using `GameTreeNode.expand` and `apply_move`.
3. `alphabeta` recursively explores this tree:
   - Stops at terminal states or when the depth limit is reached.
   - Uses `evaluate` for non-terminal leaves and `terminal_score` for finished games.
   - Propagates scores upward while updating α and β to prune branches.
4. The best root child (LEFT or RIGHT) is chosen based on the backed-up values.
5. The chosen move is **applied to the real game state** via `apply_move`, and the GUI updates.

Thus, for the concrete sequence `13213112` and depth 4, the AI "thinks" by exploring a **finite sub-tree** of possible continuations from the **current position only**, not the entire game from the original start, balancing optimality with performance.

---

