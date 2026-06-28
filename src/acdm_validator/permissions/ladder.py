"""Ordered agent action permission ladder."""

ACTION_LADDER = ("none", "read", "summarize", "recommend", "decide", "act")
ACTION_RANK = {action: rank for rank, action in enumerate(ACTION_LADDER)}


def more_restrictive(*actions: str) -> str:
    return min(actions, key=ACTION_RANK.__getitem__) if actions else "none"


def maximum_action(actions: tuple[str, ...]) -> str:
    valid = [action for action in actions if action in ACTION_RANK]
    return max(valid, key=ACTION_RANK.__getitem__) if valid else "none"
