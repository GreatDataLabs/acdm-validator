"""Risk class types and composition."""

from collections.abc import Iterable
from enum import Enum


class RiskClass(str, Enum):
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"

    @property
    def rank(self) -> int:
        return int(self.value[1:])

    @classmethod
    def parse(cls, value: object) -> "RiskClass":
        return cls(str(value).upper())


def compose_risk(values: Iterable[RiskClass]) -> RiskClass | None:
    """Return the highest input risk."""
    items = list(values)
    return max(items, key=lambda item: item.rank) if items else None
