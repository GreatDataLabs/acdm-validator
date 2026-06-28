from acdm_validator.properties import compose_provenance, normalize_provenance


def test_provenance_normalizes_and_unions():
    assert normalize_provenance(["a", "a"]) == frozenset({"a"})
    assert compose_provenance([{"a"}, {"b"}]) == frozenset({"a", "b"})
