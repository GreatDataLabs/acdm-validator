"""Level 1 completeness checks."""

from acdm_validator.contracts import EntityContract
from acdm_validator.graph import DependencyGraph
from acdm_validator.validation.finding import Finding


def completeness_findings(contracts: list[EntityContract], graph: DependencyGraph) -> list[Finding]:
    findings: list[Finding] = []
    for contract in contracts:
        entity = contract.entity_name or (contract.source.stem if contract.source else "<unknown>")
        for issue in contract.issues:
            findings.append(
                Finding(
                    "SCHEMA",
                    "L1",
                    "error",
                    entity,
                    issue.field,
                    issue.message,
                    issue.declared_value,
                    recommended_fix=f"Provide a valid {issue.field} value in the Entity Contract.",
                )
            )
    for duplicate in graph.duplicates:
        findings.append(
            Finding(
                "SCHEMA",
                "L1",
                "error",
                duplicate,
                "entity_name",
                "Entity name is declared by more than one contract.",
                duplicate,
                recommended_fix="Give every contract a unique entity_name.",
            )
        )
    for entity, missing in graph.missing.items():
        findings.append(
            Finding(
                "GRAPH",
                "L2",
                "error",
                entity,
                "depends_on",
                f"Unknown dependencies: {', '.join(missing)}.",
                list(graph.contracts[entity].depends_on),
                dependencies=missing,
                recommended_fix="Add the missing contracts or correct depends_on.",
            )
        )
    for cycle in graph.cycles:
        findings.append(
            Finding(
                "GRAPH",
                "L2",
                "error",
                cycle[0],
                "depends_on",
                f"Dependency cycle detected: {' -> '.join((*cycle, cycle[0]))}.",
                dependencies=cycle,
                recommended_fix="Remove the cycle so composition has a deterministic order.",
            )
        )
    return findings
