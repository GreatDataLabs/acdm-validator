from datetime import datetime, timezone

from acdm_validator import validate


def test_valid_contract_reaches_level_three(make_contract):
    report = validate([make_contract()])
    assert report.entity_maturity == {"member_profile": 3}


def test_current_certification_reaches_level_four(make_contract):
    contract = make_contract(
        certified_upgrade={
            "reference": "GOV-1",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    assert validate([contract]).entity_maturity["member_profile"] == 4
