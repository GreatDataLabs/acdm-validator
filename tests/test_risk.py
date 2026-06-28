from acdm_validator.properties import RiskClass, compose_risk


def test_risk_uses_highest_class():
    assert compose_risk([RiskClass.R2, RiskClass.R3]) is RiskClass.R3
