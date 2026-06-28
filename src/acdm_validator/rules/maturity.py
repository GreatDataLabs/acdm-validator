"""Conservative entity maturity scoring."""

from datetime import datetime, timezone

from acdm_validator.contracts import EntityContract
from acdm_validator.validation.finding import Finding


def _review_current(contract: EntityContract) -> bool:
    if not isinstance(contract.certified_upgrade, dict) or not contract.review_frequency_seconds:
        return False
    reviewed_at = contract.certified_upgrade.get("reviewed_at")
    if not reviewed_at:
        return False
    try:
        reviewed = datetime.fromisoformat(str(reviewed_at).replace("Z", "+00:00"))
    except ValueError:
        return False
    reviewed = reviewed.replace(tzinfo=reviewed.tzinfo or timezone.utc)
    return (
        datetime.now(timezone.utc) - reviewed
    ).total_seconds() <= contract.review_frequency_seconds


def score_maturity(contract: EntityContract, findings: list[Finding]) -> int:
    entity = contract.entity_name or (contract.source.stem if contract.source else "<unknown>")
    errors = [item for item in findings if item.entity == entity and item.severity == "error"]
    if any(item.level == "L1" for item in errors):
        return 0
    level = 1
    if contract.is_derived and any(item.level == "L2" for item in errors):
        return level
    level = 2
    if any(item.level == "L3" for item in errors):
        return level
    level = 3
    if contract.has_documented_upgrade and _review_current(contract):
        return 4
    return level
