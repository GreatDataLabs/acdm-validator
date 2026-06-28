"""Parsed ACDM Entity Contract model."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from acdm_validator.properties import (
    Cost,
    FreshnessPolicy,
    RiskClass,
    TrustTier,
    normalize_provenance,
    parse_duration,
)

from .schema import REQUIRED_FIELDS, VALID_ACTIONS, documented_upgrade


@dataclass(frozen=True)
class ContractIssue:
    field: str
    message: str
    declared_value: object = None


@dataclass
class EntityContract:
    entity_name: str | None
    business_definition: str | None
    primary_keys: tuple[str, ...]
    depends_on: tuple[str, ...]
    trust_tier: TrustTier | None
    freshness_policy: FreshnessPolicy | None
    provenance_binding: frozenset[str]
    cost: Cost | None
    risk_class: RiskClass | None
    allowed_agent_actions: tuple[str, ...]
    human_approval_required: bool | None
    downstream_exposure_rules: dict[str, Any]
    owner: str | None
    review_frequency_seconds: int | None
    certified_upgrade: object = None
    source: Path | None = None
    issues: list[ContractIssue] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def cost_class(self):  # type: ignore[no-untyped-def]
        return self.cost.cost_class if self.cost else None

    @property
    def is_derived(self) -> bool:
        return bool(self.depends_on)

    @property
    def has_documented_upgrade(self) -> bool:
        return documented_upgrade(self.certified_upgrade)

    @property
    def masking_fields(self) -> frozenset[str]:
        mask = self.downstream_exposure_rules.get("mask", [])
        return frozenset(mask) if isinstance(mask, list) else frozenset()

    @classmethod
    def from_mapping(cls, data: dict[str, Any], source: Path | None = None) -> EntityContract:
        issues: list[ContractIssue] = []
        for required in REQUIRED_FIELDS:
            if required not in data or data[required] is None:
                issues.append(
                    ContractIssue(required, "Required field is missing.", data.get(required))
                )

        def text(field_name: str) -> str | None:
            value = data.get(field_name)
            if not isinstance(value, str) or not value.strip():
                if value is not None:
                    issues.append(ContractIssue(field_name, "Must be a non-empty string.", value))
                return None
            return value.strip()

        def string_list(field_name: str, *, required: bool = True) -> tuple[str, ...]:
            value = data.get(field_name, [])
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                issues.append(
                    ContractIssue(field_name, "Must be a list of non-empty strings.", value)
                )
                return ()
            result = tuple(dict.fromkeys(item.strip() for item in value))
            if required and not result:
                issues.append(ContractIssue(field_name, "Must contain at least one value.", value))
            return result

        def parsed(field_name: str, parser):  # type: ignore[no-untyped-def]
            value = data.get(field_name)
            if value is None:
                return None
            try:
                return parser(value)
            except (TypeError, ValueError) as exc:
                issues.append(ContractIssue(field_name, str(exc), value))
                return None

        primary_keys = string_list("primary_keys")
        depends_on = string_list("depends_on", required=False)
        trust = parsed("trust_tier", TrustTier.parse)
        freshness = parsed("freshness_policy", FreshnessPolicy.from_value)
        provenance = parsed("provenance_binding", normalize_provenance) or frozenset()
        cost = parsed("cost_class", Cost.from_value)
        risk = parsed("risk_class", RiskClass.parse)

        actions = string_list("allowed_agent_actions")
        invalid_actions = sorted(set(actions) - set(VALID_ACTIONS))
        if invalid_actions:
            issues.append(
                ContractIssue(
                    "allowed_agent_actions",
                    f"Unknown actions: {', '.join(invalid_actions)}.",
                    list(actions),
                )
            )

        approval_value = data.get("human_approval_required")
        approval = approval_value if isinstance(approval_value, bool) else None
        if approval_value is not None and approval is None:
            issues.append(
                ContractIssue("human_approval_required", "Must be true or false.", approval_value)
            )

        exposure_value = data.get("downstream_exposure_rules")
        exposure: dict[str, Any] = exposure_value if isinstance(exposure_value, dict) else {}
        if exposure_value is not None and not isinstance(exposure_value, dict):
            issues.append(
                ContractIssue("downstream_exposure_rules", "Must be a mapping.", exposure_value)
            )
        if "mask" in exposure and (
            not isinstance(exposure["mask"], list)
            or not all(isinstance(item, str) and item.strip() for item in exposure["mask"])
        ):
            issues.append(
                ContractIssue(
                    "downstream_exposure_rules.mask",
                    "Must be a list of field names.",
                    exposure.get("mask"),
                )
            )

        review = parsed("review_frequency", lambda value: parse_duration(str(value)))
        return cls(
            entity_name=text("entity_name"),
            business_definition=text("business_definition"),
            primary_keys=primary_keys,
            depends_on=depends_on,
            trust_tier=trust,
            freshness_policy=freshness,
            provenance_binding=provenance,
            cost=cost,
            risk_class=risk,
            allowed_agent_actions=actions,
            human_approval_required=approval,
            downstream_exposure_rules=exposure,
            owner=text("owner"),
            review_frequency_seconds=review,
            certified_upgrade=data.get("certified_upgrade"),
            source=source,
            issues=issues,
            raw_data=dict(data),
        )
