"""Provenance normalization and composition."""

from collections.abc import Iterable


def normalize_provenance(value: object) -> frozenset[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError("provenance_binding must be a non-empty list of source identifiers")
    if not value:
        raise ValueError("provenance_binding must not be empty")
    return frozenset(item.strip() for item in value)


def compose_provenance(values: Iterable[Iterable[str]]) -> frozenset[str]:
    return frozenset(source for binding in values for source in binding)
