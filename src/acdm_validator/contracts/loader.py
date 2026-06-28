"""YAML contract loading."""

from pathlib import Path

import yaml

from acdm_validator.exceptions import ContractLoadError

from .entity_contract import EntityContract


def _contract_files(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in {".yml", ".yaml"}:
            raise ContractLoadError(f"Contract file must use .yml or .yaml: {path}")
        return [path]
    if not path.exists():
        raise ContractLoadError(f"Contract path does not exist: {path}")
    if not path.is_dir():
        raise ContractLoadError(f"Contract path is not a file or directory: {path}")
    return sorted(file for file in path.rglob("*") if file.suffix.lower() in {".yml", ".yaml"})


def load_contracts(path: str | Path) -> list[EntityContract]:
    """Load one YAML file or all YAML files beneath a directory."""
    contract_path = Path(path)
    files = _contract_files(contract_path)
    if not files:
        raise ContractLoadError(f"No YAML contracts found in {contract_path}")

    contracts: list[EntityContract] = []
    for file_path in files:
        try:
            with file_path.open(encoding="utf-8") as stream:
                data = yaml.safe_load(stream)
        except (OSError, yaml.YAMLError) as exc:
            raise ContractLoadError(f"Could not load {file_path}: {exc}") from exc
        if not isinstance(data, dict):
            raise ContractLoadError(f"Contract must be a YAML mapping: {file_path}")
        contracts.append(EntityContract.from_mapping(data, file_path))
    return contracts
