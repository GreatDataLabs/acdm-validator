"""Validation report rendering."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .finding import Finding


@dataclass
class ValidationReport:
    status: str
    entities_checked: int
    findings: list[Finding]
    entity_maturity: dict[str, int]
    data_product_maturity: int
    resolved_properties: dict[str, dict[str, Any]]
    generated_at: str

    @classmethod
    def create(
        cls,
        entities_checked: int,
        findings: list[Finding],
        entity_maturity: dict[str, int],
        resolved_properties: dict[str, dict[str, Any]],
        *,
        fail_on: str = "error",
    ) -> "ValidationReport":
        status = "failed" if should_fail(findings, fail_on) else "passed"
        maturity = min(entity_maturity.values(), default=0)
        return cls(
            status,
            entities_checked,
            findings,
            entity_maturity,
            maturity,
            resolved_properties,
            datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "entities_checked": self.entities_checked,
            "findings": [finding.to_dict() for finding in self.findings],
            "entity_maturity": self.entity_maturity,
            "data_product_maturity": self.data_product_maturity,
            "resolved_properties": self.resolved_properties,
            "generated_at": self.generated_at,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    def to_console(self) -> str:
        errors = sum(finding.severity == "error" for finding in self.findings)
        warnings = sum(finding.severity == "warning" for finding in self.findings)
        lines = [
            "ACDM Validation Report",
            f"Status: {self.status.upper()}",
            f"Entities checked: {self.entities_checked}",
            f"Findings: {errors} errors, {warnings} warnings",
            f"Maturity level: {self.data_product_maturity}",
        ]
        for finding in self.findings:
            lines.extend(
                [
                    "",
                    f"[{finding.severity.upper()}] {finding.rule_id} "
                    f"{finding.entity}.{finding.field}",
                    finding.message,
                    f"Fix: {finding.recommended_fix}" if finding.recommended_fix else "",
                ]
            )
        return "\n".join(line for line in lines if line is not None).rstrip() + "\n"


def should_fail(findings: list[Finding], fail_on: str) -> bool:
    """Apply severity or validation-stage failure policy."""
    normalized = fail_on.lower()
    if normalized == "warning":
        return any(item.severity in {"warning", "error"} for item in findings)
    if normalized == "error":
        return any(item.severity == "error" for item in findings)
    if normalized.upper() in {"L1", "L2", "L3"}:
        maximum = int(normalized[1])
        return any(
            item.severity == "error"
            and item.level.startswith("L")
            and int(item.level[1:]) <= maximum
            for item in findings
        )
    raise ValueError("fail_on must be error, warning, L1, L2, or L3")
