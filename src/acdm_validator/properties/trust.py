"""Trust tier types and composition."""

from collections.abc import Iterable
from enum import Enum


class TrustTier(str, Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"

    @property
    def rank(self) -> int:
        return int(self.value[1:])

    @classmethod
    def parse(cls, value: object) -> "TrustTier":
        return cls(str(value).upper())


def compose_trust(values: Iterable[TrustTier]) -> TrustTier | None:
    """Return the weakest (largest-ranked) input tier."""
    items = list(values)
    return max(items, key=lambda item: item.rank) if items else None
