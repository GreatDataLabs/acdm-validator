"""Level 2 composition resolution and R1-R5, R7-R8 checks."""

from dataclasses import dataclass
from typing import Any

from acdm_validator.contracts import EntityContract
from acdm_validator.properties import (
    Cost,
    FreshnessPolicy,
    RiskClass,
    TrustTier,
    compose_cost,
    compose_freshness,
    compose_provenance,
    compose_risk,
    compose_trust,
)
from acdm_validator.validation.finding import Finding

from .rule_ids import (
    R1_TRUST,
    R2_FRESHNESS,
    R3_PROVENANCE,
    R4_COST,
    R5_RISK,
    R7_EXPIRED,
    R8_MASKING,
)


@dataclass
class ResolvedProperties:
    trust: TrustTier | None
    freshness: FreshnessPolicy | None
    provenance: frozenset[str]
    cost: Cost | None
    risk: RiskClass | None
    masks: frozenset[str]
    permission_ceiling: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "trust_tier": self.trust.value if self.trust else None,
            "freshness_policy": self.freshness.to_dict() if self.freshness else None,
            "provenance_binding": sorted(self.provenance),
            "cost": self.cost.to_dict() if self.cost else None,
            "risk_class": self.risk.value if self.risk else None,
            "mask": sorted(self.masks),
            "permission_ceiling": self.permission_ceiling,
        }


def _finding(
    rule: str,
    contract: EntityContract,
    field: str,
    message: str,
    declared: object,
    computed: object,
    fix: str,
) -> Finding:
    return Finding(
        rule,
        "L2",
        "error",
        contract.entity_name or "<unknown>",
        field,
        message,
        declared,
        computed,
        contract.depends_on,
        fix,
    )


def resolve_and_check(
    contract: EntityContract, dependencies: list[ResolvedProperties]
) -> tuple[ResolvedProperties, list[Finding], bool]:
    """Resolve effective properties and return findings plus an upgrade flag."""
    if not contract.is_derived or not dependencies:
        return (
            ResolvedProperties(
                contract.trust_tier,
                contract.freshness_policy,
                contract.provenance_binding,
                contract.cost,
                contract.risk_class,
                contract.masking_fields,
            ),
            [],
            False,
        )

    findings: list[Finding] = []
    trust = compose_trust(item.trust for item in dependencies if item.trust)
    freshness = compose_freshness(item.freshness for item in dependencies if item.freshness)
    provenance = compose_provenance(item.provenance for item in dependencies)
    cost = compose_cost(item.cost for item in dependencies if item.cost)
    risk = compose_risk(item.risk for item in dependencies if item.risk)
    masks = compose_provenance(item.masks for item in dependencies)
    upgrade_attempted = False
    certified = contract.has_documented_upgrade

    if contract.trust_tier and trust and contract.trust_tier.rank < trust.rank:
        upgrade_attempted = True
        if not certified:
            findings.append(
                _finding(
                    R1_TRUST,
                    contract,
                    "trust_tier",
                    "Declared trust tier is better than the weakest dependency trust tier.",
                    contract.trust_tier.value,
                    trust.value,
                    f"Change trust_tier to {trust.value} or provide a documented "
                    "certified_upgrade.",
                )
            )
    if contract.freshness_policy and freshness:
        looser = contract.freshness_policy.max_age_seconds > freshness.max_age_seconds
        if looser:
            upgrade_attempted = True
            if not certified:
                findings.append(
                    _finding(
                        R2_FRESHNESS,
                        contract,
                        "freshness_policy",
                        "Declared maximum age is looser than the strictest dependency policy.",
                        contract.freshness_policy.to_dict(),
                        freshness.to_dict(),
                        "Use the strictest dependency max_age or document a certified upgrade.",
                    )
                )
        if freshness.is_expired() and not contract.freshness_policy.is_expired():
            findings.append(
                _finding(
                    R7_EXPIRED,
                    contract,
                    "freshness_policy",
                    "An expired dependency makes the derived entity expired until refreshed.",
                    contract.freshness_policy.to_dict(),
                    {**freshness.to_dict(), "expired": True},
                    "Refresh the inputs and derivative, or declare the derivative expired.",
                )
            )
    missing_sources = provenance - contract.provenance_binding
    if missing_sources:
        findings.append(
            _finding(
                R3_PROVENANCE,
                contract,
                "provenance_binding",
                f"Missing contributing sources: {', '.join(sorted(missing_sources))}.",
                sorted(contract.provenance_binding),
                sorted(provenance),
                "Add every contributing source to provenance_binding.",
            )
        )
    if contract.cost and cost:
        class_low = contract.cost.cost_class.rank < cost.cost_class.rank
        budget_low = (
            contract.cost.budget is not None
            and cost.budget is not None
            and contract.cost.budget < cost.budget
        )
        if class_low or budget_low:
            findings.append(
                _finding(
                    R4_COST,
                    contract,
                    "cost_class",
                    "Declared cost does not reflect accumulated dependency cost.",
                    contract.cost.to_dict(),
                    cost.to_dict(),
                    "Raise the cost class or budget to the accumulated dependency cost.",
                )
            )
    if contract.risk_class and risk and contract.risk_class.rank < risk.rank:
        upgrade_attempted = True
        if not certified:
            findings.append(
                _finding(
                    R5_RISK,
                    contract,
                    "risk_class",
                    "Declared risk class is lower than the highest dependency risk class.",
                    contract.risk_class.value,
                    risk.value,
                    f"Change risk_class to {risk.value} or provide a documented certified_upgrade.",
                )
            )
    missing_masks = masks - contract.masking_fields
    if missing_masks and not certified:
        findings.append(
            _finding(
                R8_MASKING,
                contract,
                "downstream_exposure_rules.mask",
                f"Required masks were not propagated: {', '.join(sorted(missing_masks))}.",
                sorted(contract.masking_fields),
                sorted(masks),
                "Propagate every dependency mask or document a certified exception.",
            )
        )

    effective_trust = contract.trust_tier
    if trust and (
        not contract.trust_tier or (contract.trust_tier.rank < trust.rank and not certified)
    ):
        effective_trust = trust
    effective_risk = contract.risk_class
    if risk and (
        not contract.risk_class or (contract.risk_class.rank < risk.rank and not certified)
    ):
        effective_risk = risk
    effective_freshness = contract.freshness_policy
    if freshness:
        if (
            not contract.freshness_policy
            or contract.freshness_policy.max_age_seconds > freshness.max_age_seconds
            and not certified
        ):
            effective_freshness = freshness
        elif freshness.is_expired():
            effective_freshness = FreshnessPolicy(
                effective_freshness.max_age_seconds,
                effective_freshness.as_of,
                True,
            )
    effective_cost = contract.cost
    if cost and (
        not contract.cost
        or contract.cost.cost_class.rank < cost.cost_class.rank
        or (
            contract.cost.budget is not None
            and cost.budget is not None
            and contract.cost.budget < cost.budget
        )
    ):
        effective_cost = cost
    return (
        ResolvedProperties(
            effective_trust,
            effective_freshness,
            provenance | contract.provenance_binding,
            effective_cost,
            effective_risk,
            masks | contract.masking_fields,
        ),
        findings,
        upgrade_attempted,
    )
