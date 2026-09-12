# Git Delivery Workflow

The project uses a strict Git workflow to maintain a clean, audit-ready history of scientific progress.

## Branching Strategy
- **Default Branch**: The source of truth.
- **Task Branches**: Work is performed in `codex/<topic>` branches.
- **Integration**: Fast-forward merges are preferred. If not possible, a merge commit is used.

## Commit Standards
- **Cohesion**: Commits must be cohesive. Scientific implementation should be separated from instruction maintenance.
- **Verification**: No commit is made until the task is validated (tests pass, results verified).
- **Delivery**: After integration, the task branch is deleted.

## PR Requirements
Pull Request descriptions must include:
- The scientific objective.
- Changed equations or conventions.
- Implementation choices and validation commands/results.
- Convergence/sensitivity evidence.
- Output paths and Zeus resource implications.
