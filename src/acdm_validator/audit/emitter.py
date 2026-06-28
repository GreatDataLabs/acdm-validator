"""Governance audit record generation."""

import json
from pathlib import Path
from typing import Any

from acdm_validator.validation import ValidationReport
from acdm_validator.version import __version__

from .openlineage import openlineage_facet
from .opentelemetry import opentelemetry_attributes


def build_audit_record(
    report: ValidationReport,
    *,
    include_openlineage: bool = False,
    include_opentelemetry: bool = False,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "validator": {"name": "acdm-validator", "version": __version__},
        "validation_timestamp": report.generated_at,
        "status": report.status,
        "data_product_maturity": report.data_product_maturity,
        "entity_maturity": report.entity_maturity,
        "resolved_entities": report.resolved_properties,
        "dependency_composition": {
            entity: {"resolved": properties}
            for entity, properties in report.resolved_properties.items()
        },
        "findings": [finding.to_dict() for finding in report.findings],
    }
    if include_openlineage:
        record["openlineage_facet"] = openlineage_facet(report.resolved_properties)
    if include_opentelemetry:
        record["opentelemetry_attributes"] = opentelemetry_attributes(report)
    return record


def write_audit_record(report: ValidationReport, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(build_audit_record(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
