"""Permission ceiling composition."""

from acdm_validator.contracts import EntityContract
from acdm_validator.rules.composition import ResolvedProperties

from .decision_matrix import property_ceiling
from .ladder import more_restrictive


def compute_permission_ceiling(
    contract: EntityContract,
    resolved: ResolvedProperties,
    dependency_ceilings: list[str] | None = None,
) -> str:
    local = property_ceiling(contract, resolved)
    return more_restrictive(local, *(dependency_ceilings or []))
