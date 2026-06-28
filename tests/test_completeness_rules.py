from acdm_validator import validate
from acdm_validator.contracts import EntityContract


def test_missing_required_field_is_l1_finding(base_mapping):
    del base_mapping["owner"]
    report = validate([EntityContract.from_mapping(base_mapping)])
    assert report.entity_maturity["member_profile"] == 0
    assert any(item.level == "L1" and item.field == "owner" for item in report.findings)


def test_invalid_enum_and_action_are_findings(base_mapping):
    base_mapping.update(trust_tier="T9", allowed_agent_actions=["read", "launch"])
    report = validate([EntityContract.from_mapping(base_mapping)])
    fields = {item.field for item in report.findings}
    assert {"trust_tier", "allowed_agent_actions"} <= fields
