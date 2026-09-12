# Implementation & Validation Standards

The codebase follows a strict engineering standard to ensure that scientific results are not confounded by software bugs.

## SOLID Design Principles
All new and modified code must adhere to:
- **Single Responsibility**: Separate models, solvers, configuration, I/O, and plotting.
- **Open/Closed**: Extend behavior via composition/strategies rather than sprawling conditionals.
- **Liskov Substitution**: Alternative implementations must honor the same contract (units, normalization).
- **Interface Segregation**: Expose only the capabilities each caller needs.
- **Dependency Inversion**: Keep scientific policy independent of concrete solver/storage implementations.

## Python Conventions
- **Standards**: PEP 8, type hints for public interfaces, and `pathlib.Path`.
- **Forbidden**: Mutable defaults, wildcard imports, and hidden caches.
- **Environment**: Python 3.11 (matching Zeus HPC).

## Validation Workflow
Before delivery, every change must be verified:
1. `python -m py_compile` for syntax.
2. `--help` check for CLI orchestration.
3. `pytest` for unit and regression tests.
4. **Regression First**: For bugs, a failing test must be added before the fix.

See also: [[production-pipeline]].
