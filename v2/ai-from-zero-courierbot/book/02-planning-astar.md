# Meeting 2 — Planning Upgrade (BFS → A*)

## Central question

How can an agent decide systematically instead of “vibing”?

This meeting treats navigation as a **search problem**: the map is a graph, and planning is pathfinding.

---

## Glossary (minimal)

- **State space:** the set of possible states (here: grid positions).
- **Transition:** what happens when you take an action (move N/S/E/W).
- **Frontier:** the boundary between explored and unexplored states during search.
- **Heuristic:** a fast estimate of remaining distance to the goal.
- **A\* search:** a best-first search using `f(n) = g(n) + h(n)`.

---

## Graph view of a grid

Every free cell is a node. Edges connect neighboring cells.

- BFS (Breadth-First Search) guarantees shortest paths in unweighted graphs.
- A\* uses a heuristic to explore fewer nodes while preserving optimality (with an admissible heuristic).

In this repository:
- `learning_compiler/planning/search.py` implements BFS and A\*.
- `learning_compiler/agent/lab2.py` uses A\* to compute a plan.

---

## A\* loop (pseudocode)

```text
frontier = priority queue ordered by f = g + h
g[start] = 0
push(start, f=0)

while frontier not empty:
  current = pop_min_f(frontier)
  if current == goal: return path
  for neighbor in neighbors(current):
    tentative_g = g[current] + 1
    if neighbor not seen OR tentative_g < g[neighbor]:
      came_from[neighbor] = current
      g[neighbor] = tentative_g
      f = tentative_g + heuristic(neighbor, goal)
      push(neighbor, f)
```

---

## Worked example (intuition)

Heuristic: Manhattan distance.

If the goal is far to the east, A\* prefers moves that reduce east-west distance, but it still explores
alternatives when obstacles force detours.

---

## Analogy

Planning is like using a **GPS**:
- BFS is “drive every street in expanding circles.”
- A\* is “drive where the GPS thinks you should go, but keep a backup plan if you hit traffic.”

---

## Exercise

1. Run `python scripts/run_lab2.py --seed 1`.
2. In the journal, find the first time the agent writes planning stats in its snapshot.
3. Compare:
   - total steps,
   - number of planner expansions,
   between the obstacle map and the toy map.
