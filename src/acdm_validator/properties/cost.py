"""Cost class and conservative additive composition."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class CostClass(str, Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"

    @property
    def rank(self) -> int:
        return int(self.value[1:])

    @classmethod
    def from_rank(cls, rank: int) -> "CostClass":
        return cls(f"C{min(4, max(1, rank))}")


@dataclass(frozen=True)
class Cost:
    cost_class: CostClass
    budget: float | None = None

    @classmethod
    def from_value(cls, value: object) -> "Cost":
        if isinstance(value, str):
            return cls(CostClass(value.upper()))
        if not isinstance(value, dict):
            raise ValueError("cost_class must be C1-C4 or a mapping with class and budget")
        class_value = value.get("class", value.get("cost_class"))
        budget_value = value.get("budget")
        budget = float(budget_value) if budget_value is not None else None
        if budget is not None and budget < 0:
            raise ValueError("cost budget must be non-negative")
        return cls(CostClass(str(class_value).upper()), budget)

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {"class": self.cost_class.value, "rank": self.cost_class.rank}
        if self.budget is not None:
            result["budget"] = self.budget
        return result


def compose_cost(values: Iterable[Cost]) -> Cost | None:
    """Accumulate class ranks and numeric budgets conservatively."""
    items = list(values)
    if not items:
        return None
    budgets = [item.budget for item in items]
    return Cost(
        CostClass.from_rank(sum(item.cost_class.rank for item in items)),
        sum(item for item in budgets if item is not None)
        if all(item is not None for item in budgets)
        else None,
    )
