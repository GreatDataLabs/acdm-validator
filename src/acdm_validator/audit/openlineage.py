"""Optional OpenLineage-compatible facet projection."""

from typing import Any


def openlineage_facet(resolved_properties: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "_producer": "https://github.com/ravikiranpagidi/acdm-validator",
        "_schemaURL": "https://github.com/ravikiranpagidi/acdm-validator/blob/main/SPEC.md",
        "entities": resolved_properties,
    }
