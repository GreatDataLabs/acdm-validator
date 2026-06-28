from acdm_validator.properties import TrustTier, compose_trust


def test_trust_uses_weakest_tier():
    assert compose_trust([TrustTier.T1, TrustTier.T3]) is TrustTier.T3


def test_trust_parsing_is_case_insensitive():
    assert TrustTier.parse("t2") is TrustTier.T2
