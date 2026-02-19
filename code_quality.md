## Code quality and style rules (staff-level defaults)

### General
- Default to staff-level engineering quality.
- Optimize for readability and maintainability by a new teammate.
- Prefer simple, explicit control flow and single-responsibility design.
- Leave the codebase better than you found it (reduce complexity in touched areas).

### Project structure
- Package-first:
  - `scripts/` contains thin executable wrappers only.
  - reusable logic lives under `learning_compiler/`, organized by domain (e.g., `agent/`, `orchestration/`, `validator/`).
- Keep CLI entrypoints thin; move business logic into importable modules.

### Module boundaries and size
- Modules SHOULD stay cohesive and reviewable (guideline: ~<= 250 LOC).
- If a module grows large, split by responsibility (types/fs/stage/commands/etc.).

### Python and typing
- Python 3.11 only.
- Types MUST be strict (`mypy --strict`); avoid `Any` unless isolated at boundaries.
- Avoid stringly-typed behavior: new protocol fields MUST be modeled explicitly.
- Prefer:
  - `@dataclass(slots=True, frozen=True)` for immutable value/protocol objects (when appropriate).
  - `Enum` for closed sets (phases, effects, profiles, violation types).
  - `Literal` / `NewType` / `TypedDict` where they encode real invariants.

### Purity, I/O, and side effects
- Modules MUST be safe to import: no import-time side effects.
- Keep I/O at the edges; core logic SHOULD be pure/portable when possible.
- No hidden global state; pass dependencies explicitly (RNG, config, clients).

### Determinism
- Determinism is a feature:
  - use a seeded RNG (`random.Random(seed)`) or the existing `FaultPlan`.
  - do not use global randomness.
  - keep replay/trace hashes stable when expected.

### Errors and APIs
- Use explicit error contracts:
  - prefer small project exception types.
  - no bare `except`.
  - no silent `None`/`False` failures as control flow.
- Keep public APIs small and stable; keep helpers private (prefix `_`).

### Design style
- Prefer composition + `Protocol` interfaces over deep inheritance.

### Documentation
- Keep functions small; keep modules cohesive.
- Write short docstrings when intent/constraints are non-obvious.