from copy import deepcopy

import pytest

from acdm_validator.contracts import EntityContract


@pytest.fixture
def base_mapping():
    return {
        "entity_name": "member_profile",
        "business_definition": "A governed member profile.",
        "primary_keys": ["member_id"],
        "trust_tier": "T1",
        "freshness_policy": {"max_age": "24h"},
        "provenance_binding": ["member_db"],
        "cost_class": "C1",
        "risk_class": "R1",
        "allowed_agent_actions": ["read", "summarize"],
        "human_approval_required": False,
        "downstream_exposure_rules": {"mask": []},
        "owner": "member-data-team",
        "review_frequency": "30d",
        "certified_upgrade": None,
    }


@pytest.fixture
def make_contract(base_mapping):
    def factory(**updates):
        mapping = deepcopy(base_mapping)
        mapping.update(updates)
        return EntityContract.from_mapping(mapping)

    return factory
