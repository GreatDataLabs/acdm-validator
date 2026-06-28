from acdm_validator.graph import DependencyGraph


def test_dependency_first_order(make_contract):
    leaf = make_contract()
    derived = make_contract(entity_name="derived", depends_on=["member_profile"])
    graph = DependencyGraph([derived, leaf])
    assert [item.entity_name for item in graph.topological_order()] == ["member_profile", "derived"]


def test_missing_dependency_and_cycle_are_detected(make_contract):
    one = make_contract(entity_name="one", depends_on=["two", "absent"])
    two = make_contract(entity_name="two", depends_on=["one"])
    graph = DependencyGraph([one, two])
    assert graph.missing == {"one": ("absent",)}
    assert graph.cycles == [("one", "two")]
