"""Structured validation findings."""

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Finding:
    rule_id: str
    level: str
    severity: str
    entity: str
    field: str
    message: str
    declared_value: Any = None
    computed_value: Any = None
    dependencies: tuple[str, ...] = ()
    recommended_fix: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = _json_safe(asdict(self))
        result["dependencies"] = list(self.dependencies)
        return result


def _json_safe(value: Any) -> Any:
    """Convert loader values into deterministic JSON-compatible structures."""
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        converted = [_json_safe(item) for item in value]
        return sorted(converted, key=str) if isinstance(value, (set, frozenset)) else converted
    return str(value)
