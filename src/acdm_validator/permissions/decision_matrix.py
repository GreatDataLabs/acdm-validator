"""Default, deliberately conservative ACDM permission matrix."""

from acdm_validator.contracts import EntityContract
from acdm_validator.rules.composition import ResolvedProperties

from .ladder import more_restrictive


def property_ceiling(contract: EntityContract, resolved: ResolvedProperties) -> str:
    """Compute the maximum action supported by resolved governance properties."""
    if not resolved.trust or not resolved.risk or not resolved.freshness:
        return "none"

    if resolved.trust.rank == 4:
        ceiling = "read"
    elif resolved.trust.rank == 3:
        ceiling = "recommend" if contract.human_approval_required else "summarize"
    elif resolved.trust.rank == 1 and resolved.risk.rank == 1:
        ceiling = "decide"
    else:
        ceiling = "recommend"

    if resolved.risk.rank == 4 or resolved.risk.rank == 3:
        ceiling = more_restrictive(
            ceiling, "recommend" if contract.human_approval_required else "summarize"
        )
    if resolved.freshness.is_expired():
        ceiling = more_restrictive(ceiling, "summarize")
    if not resolved.provenance:
        ceiling = more_restrictive(ceiling, "summarize")
    if resolved.cost and resolved.cost.cost_class.rank == 4:
        ceiling = more_restrictive(ceiling, "summarize")
    if resolved.masks:
        ceiling = more_restrictive(ceiling, "recommend")
    return ceiling
