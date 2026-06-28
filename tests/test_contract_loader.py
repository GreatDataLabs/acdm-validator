from pathlib import Path

import pytest

from acdm_validator import load_contracts
from acdm_validator.exceptions import ContractLoadError
from acdm_validator.properties import TrustTier


def test_loads_yaml_contract(tmp_path: Path, base_mapping):
    import yaml

    path = tmp_path / "contract.yml"
    path.write_text(yaml.safe_dump(base_mapping), encoding="utf-8")
    contract = load_contracts(path)[0]
    assert contract.entity_name == "member_profile"
    assert contract.trust_tier is TrustTier.T1


def test_directory_is_recursive_and_sorted(tmp_path: Path, base_mapping):
    import yaml

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.yaml").write_text(yaml.safe_dump(base_mapping), encoding="utf-8")
    changed = {**base_mapping, "entity_name": "account"}
    (tmp_path / "a.yml").write_text(yaml.safe_dump(changed), encoding="utf-8")
    assert [item.entity_name for item in load_contracts(tmp_path)] == ["account", "member_profile"]


def test_non_mapping_yaml_is_a_load_error(tmp_path: Path):
    path = tmp_path / "bad.yml"
    path.write_text("- not\n- a\n- contract\n", encoding="utf-8")
    with pytest.raises(ContractLoadError):
        load_contracts(path)
