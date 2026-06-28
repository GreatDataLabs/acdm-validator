from acdm_validator.permissions import compute_permission_ceiling
from acdm_validator.rules.composition import ResolvedProperties


def test_t4_caps_at_read(make_contract):
    contract = make_contract(trust_tier="T4")
    resolved = ResolvedProperties(
        contract.trust_tier,
        contract.freshness_policy,
        contract.provenance_binding,
        contract.cost,
        contract.risk_class,
        frozenset(),
    )
    assert compute_permission_ceiling(contract, resolved) == "read"


def test_dependency_ceiling_is_never_exceeded(make_contract):
    contract = make_contract()
    resolved = ResolvedProperties(
        contract.trust_tier,
        contract.freshness_policy,
        contract.provenance_binding,
        contract.cost,
        contract.risk_class,
        frozenset(),
    )
    assert compute_permission_ceiling(contract, resolved, ["summarize"]) == "summarize"
