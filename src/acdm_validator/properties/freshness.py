"""Freshness policy parsing and composition."""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

_DURATION = re.compile(r"^(?P<amount>\d+(?:\.\d+)?)(?P<unit>s|m|h|d|w)$", re.IGNORECASE)
_MULTIPLIERS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def parse_duration(value: str) -> int:
    """Parse a compact duration such as ``24h`` into whole seconds."""
    match = _DURATION.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Invalid duration {value!r}; expected a value such as '24h' or '7d'.")
    return int(float(match.group("amount")) * _MULTIPLIERS[match.group("unit").lower()])


def format_duration(seconds: int) -> str:
    for unit, size in (("w", 604800), ("d", 86400), ("h", 3600), ("m", 60)):
        if seconds % size == 0:
            return f"{seconds // size}{unit}"
    return f"{seconds}s"


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        result = value
    else:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return result.replace(tzinfo=result.tzinfo or timezone.utc)


@dataclass(frozen=True)
class FreshnessPolicy:
    max_age_seconds: int
    as_of: datetime | None = None
    declared_expired: bool = False

    @classmethod
    def from_value(cls, value: object) -> "FreshnessPolicy":
        if isinstance(value, str):
            return cls(parse_duration(value))
        if not isinstance(value, dict):
            raise ValueError("freshness_policy must be a mapping or duration string")
        max_age = value.get("max_age")
        if not isinstance(max_age, str):
            raise ValueError("freshness_policy.max_age must be a duration string")
        as_of = _parse_timestamp(value["as_of"]) if value.get("as_of") else None
        return cls(parse_duration(max_age), as_of, bool(value.get("expired", False)))

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.declared_expired:
            return True
        if self.as_of is None:
            return False
        current = now or datetime.now(timezone.utc)
        return (current - self.as_of).total_seconds() > self.max_age_seconds

    def to_dict(self, now: datetime | None = None) -> dict[str, object]:
        result: dict[str, object] = {
            "max_age": format_duration(self.max_age_seconds),
            "max_age_seconds": self.max_age_seconds,
            "expired": self.is_expired(now),
        }
        if self.as_of:
            result["as_of"] = self.as_of.isoformat()
        return result


def compose_freshness(values: Iterable[FreshnessPolicy]) -> FreshnessPolicy | None:
    """Return the most restrictive policy, propagating expired state."""
    items = list(values)
    if not items:
        return None
    strictest = min(items, key=lambda item: item.max_age_seconds)
    as_of_values = [item.as_of for item in items if item.as_of]
    return FreshnessPolicy(
        max_age_seconds=strictest.max_age_seconds,
        as_of=min(as_of_values) if as_of_values else None,
        declared_expired=any(item.is_expired() for item in items),
    )
