import json
from datetime import date
from pathlib import Path

from acdm_validator import validate_contracts
from acdm_validator.audit import build_audit_record

ROOT = Path(__file__).parents[1]


def test_clean_and_failing_examples():
    clean = validate_contracts(str(ROOT / "examples/contracts/clean_join"))
    failing = validate_contracts(str(ROOT / "examples/contracts/failing_join"))
    assert clean.status == "passed"
    assert clean.data_product_maturity == 3
    assert failing.status == "failed"
    assert failing.data_product_maturity == 1


def test_json_report_and_audit_are_serializable():
    report = validate_contracts(str(ROOT / "examples/contracts/clean_join"))
    payload = json.loads(report.to_json())
    audit = build_audit_record(report, include_openlineage=True, include_opentelemetry=True)
    assert payload["entities_checked"] == 3
    assert audit["validator"]["version"] == "0.1.0"
    assert "openlineage_facet" in audit
    json.dumps(audit)


def test_malformed_yaml_scalar_still_serializes(base_mapping):
    from acdm_validator import validate
    from acdm_validator.contracts import EntityContract

    base_mapping["owner"] = date(2026, 6, 28)
    report = validate([EntityContract.from_mapping(base_mapping)])
    assert json.loads(report.to_json())["findings"][0]["declared_value"] == "2026-06-28"
