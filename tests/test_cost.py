from acdm_validator.properties import Cost, CostClass, compose_cost


def test_cost_rank_and_budget_accumulate():
    result = compose_cost([Cost(CostClass.C1, 5), Cost(CostClass.C2, 7)])
    assert result == Cost(CostClass.C3, 12)


def test_cost_class_caps_at_c4():
    result = compose_cost([Cost(CostClass.C3), Cost(CostClass.C3)])
    assert result and result.cost_class is CostClass.C4
