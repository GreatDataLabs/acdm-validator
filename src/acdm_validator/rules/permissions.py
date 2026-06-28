"""Level 3 permission, certification, and conflict checks."""

from acdm_validator.contracts import EntityContract
from acdm_validator.permissions import ACTION_RANK, maximum_action
from acdm_validator.rules.composition import ResolvedProperties
from acdm_validator.validation.finding import Finding

from .rule_ids import R6_PERMISSION, R9_CERTIFICATION, R10_CONFLICT


def permission_findings(
    contract: EntityContract,
    resolved: ResolvedProperties,
    *,
    upgrade_attempted: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    entity = contract.entity_name or "<unknown>"
    maximum = maximum_action(contract.allowed_agent_actions)
    if ACTION_RANK.get(maximum, 0) > ACTION_RANK[resolved.permission_ceiling]:
        findings.append(
            Finding(
                R6_PERMISSION,
                "L3",
                "error",
                entity,
                "allowed_agent_actions",
                f"Declared action '{maximum}' exceeds the computed permission ceiling "
                f"'{resolved.permission_ceiling}'.",
                list(contract.allowed_agent_actions),
                resolved.permission_ceiling,
                contract.depends_on,
                f"Remove actions above {resolved.permission_ceiling} or correct the "
                "governing properties.",
            )
        )
        if contract.is_derived:
            findings.append(
                Finding(
                    R10_CONFLICT,
                    "L3",
                    "error",
                    entity,
                    "allowed_agent_actions",
                    "Composition produces a permission ceiling below the contract's "
                    "declared action.",
                    maximum,
                    resolved.permission_ceiling,
                    contract.depends_on,
                    "Align declared permissions with the composed dependency constraints.",
                )
            )
    if upgrade_attempted and not contract.has_documented_upgrade:
        findings.append(
            Finding(
                R9_CERTIFICATION,
                "L3",
                "error",
                entity,
                "certified_upgrade",
                "A property upgrade beyond the computed default is not documented.",
                contract.certified_upgrade,
                "documented certification reference",
                contract.depends_on,
                "Add certification documentation or remove the property upgrade.",
            )
        )
    if (
        contract.certified_upgrade is not None
        and not contract.has_documented_upgrade
        and not any(finding.rule_id == R9_CERTIFICATION for finding in findings)
    ):
        findings.append(
            Finding(
                R9_CERTIFICATION,
                "L3",
                "error",
                entity,
                "certified_upgrade",
                "certified_upgrade is present but has no documentation reference.",
                contract.certified_upgrade,
                "documentation, reference, reason, URL, or ticket",
                contract.depends_on,
                "Add a durable certification reference.",
            )
        )
    return findings
