"""Single-pass ACDM validation engine used by both API and CLI."""

from acdm_validator.contracts import EntityContract, load_contracts
from acdm_validator.graph import DependencyGraph
from acdm_validator.permissions import compute_permission_ceiling
from acdm_validator.rules.completeness import completeness_findings
from acdm_validator.rules.composition import ResolvedProperties, resolve_and_check
from acdm_validator.rules.maturity import score_maturity
from acdm_validator.rules.permissions import permission_findings

from .report import ValidationReport


def validate(contracts: list[EntityContract], *, fail_on: str = "error") -> ValidationReport:
    """Validate parsed contracts and return a structured report."""
    graph = DependencyGraph(contracts)
    findings = completeness_findings(contracts, graph)
    resolved: dict[str, ResolvedProperties] = {}
    upgrade_attempts: dict[str, bool] = {}
    cycle_entities = {name for cycle in graph.cycles for name in cycle}

    for contract in graph.topological_order():
        name = contract.entity_name
        if not name:
            continue
        dependency_values = [resolved[dep] for dep in contract.depends_on if dep in resolved]
        graph_blocked = name in graph.missing or name in cycle_entities
        schema_blocked = bool(contract.issues)
        if graph_blocked or schema_blocked:
            properties, _, attempted = resolve_and_check(contract, [])
        else:
            properties, composition_issues, attempted = resolve_and_check(
                contract, dependency_values
            )
            findings.extend(composition_issues)
        dependency_ceilings = [
            resolved[dep].permission_ceiling for dep in contract.depends_on if dep in resolved
        ]
        properties.permission_ceiling = compute_permission_ceiling(
            contract, properties, dependency_ceilings
        )
        resolved[name] = properties
        upgrade_attempts[name] = attempted

    for contract in graph.topological_order():
        name = contract.entity_name
        if (
            not name
            or name not in resolved
            or contract.issues
            or name in graph.missing
            or name in cycle_entities
        ):
            continue
        findings.extend(
            permission_findings(
                contract,
                resolved[name],
                upgrade_attempted=upgrade_attempts.get(name, False),
            )
        )

    findings.sort(key=lambda item: (item.entity, item.level, item.rule_id, item.field))
    maturity: dict[str, int] = {}
    for contract in contracts:
        entity = contract.entity_name or (contract.source.stem if contract.source else "<unknown>")
        maturity[entity] = score_maturity(contract, findings)

    return ValidationReport.create(
        len(contracts),
        findings,
        maturity,
        {
            name: {
                **properties.to_dict(),
                "depends_on": list(graph.contracts[name].depends_on),
            }
            for name, properties in sorted(resolved.items())
        },
        fail_on=fail_on,
    )


def validate_contracts(path: str, fail_on: str = "error") -> ValidationReport:
    """Load and validate contracts from a YAML file or directory."""
    return validate(load_contracts(path), fail_on=fail_on)
