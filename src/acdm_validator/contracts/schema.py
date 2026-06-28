"""Entity Contract schema constants and lightweight normalization helpers."""

REQUIRED_FIELDS = (
    "entity_name",
    "business_definition",
    "primary_keys",
    "trust_tier",
    "freshness_policy",
    "provenance_binding",
    "cost_class",
    "risk_class",
    "allowed_agent_actions",
    "human_approval_required",
    "downstream_exposure_rules",
    "owner",
    "review_frequency",
)

VALID_ACTIONS = ("none", "read", "summarize", "recommend", "decide", "act")


def documented_upgrade(value: object) -> bool:
    """Return whether certification metadata includes a usable documentation reference."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        keys = ("documentation", "reference", "reason", "url", "ticket")
        return any(bool(value.get(key)) for key in keys)
    return False
