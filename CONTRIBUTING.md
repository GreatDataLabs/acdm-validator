# Contributing

Thank you for helping make ACDM contracts easier to govern. Open an issue before a large behavioral
change so rule semantics can be agreed first.

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
python -m pip install -e ".[dev]"
ruff check .
pytest
```

Add tests for every rule change, keep public APIs typed, and document any governance interpretation.
By contributing, you agree that your work is licensed under the repository's MIT License.

