"""Optional OpenTelemetry attribute projection."""

from acdm_validator.validation import ValidationReport


def opentelemetry_attributes(report: ValidationReport) -> dict[str, object]:
    return {
        "acdm.validation.status": report.status,
        "acdm.validation.entities_checked": report.entities_checked,
        "acdm.validation.findings": len(report.findings),
        "acdm.validation.maturity": report.data_product_maturity,
    }
