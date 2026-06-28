from acdm_validator import validate


def _derived(make_contract, **updates):
    defaults = {
        "entity_name": "derived",
        "depends_on": ["member_profile", "vendor"],
        "trust_tier": "T1",
        "freshness_policy": {"max_age": "48h"},
        "provenance_binding": ["member_db"],
        "cost_class": "C1",
        "risk_class": "R1",
        "downstream_exposure_rules": {"mask": []},
    }
    defaults.update(updates)
    return make_contract(**defaults)


def test_r1_to_r5_and_r8_are_reported(make_contract):
    member = make_contract(downstream_exposure_rules={"mask": ["ssn"]})
    vendor = make_contract(
        entity_name="vendor",
        trust_tier="T3",
        freshness_policy={"max_age": "12h"},
        provenance_binding=["vendor_api"],
        risk_class="R3",
    )
    report = validate([member, vendor, _derived(make_contract)])
    ids = {finding.rule_id for finding in report.findings}
    assert {"R1", "R2", "R3", "R4", "R5", "R8"} <= ids


def test_r7_expired_input_propagates(make_contract):
    expired = make_contract(freshness_policy={"max_age": "24h", "expired": True})
    derived = make_contract(
        entity_name="derived",
        depends_on=["member_profile"],
        freshness_policy={"max_age": "24h"},
        cost_class="C1",
    )
    report = validate([expired, derived])
    assert "R7" in {finding.rule_id for finding in report.findings}
    assert report.resolved_properties["derived"]["freshness_policy"]["expired"] is True


def test_documented_upgrade_allows_trust_and_risk_upgrade(make_contract):
    source = make_contract(trust_tier="T3", risk_class="R3")
    derived = make_contract(
        entity_name="derived",
        depends_on=["member_profile"],
        trust_tier="T1",
        risk_class="R1",
        cost_class="C1",
        certified_upgrade={"reference": "GOV-1"},
    )
    report = validate([source, derived])
    assert not {"R1", "R5", "R9"} & {finding.rule_id for finding in report.findings}
