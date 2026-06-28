from datetime import datetime, timedelta, timezone

import pytest

from acdm_validator.properties import FreshnessPolicy, compose_freshness, parse_duration


def test_duration_parsing():
    assert parse_duration("24h") == 86400
    assert parse_duration("7d") == 604800


def test_invalid_duration_is_rejected():
    with pytest.raises(ValueError):
        parse_duration("tomorrow")


def test_freshness_composes_strictest_and_expired():
    expired = FreshnessPolicy(86400, datetime.now(timezone.utc) - timedelta(days=2))
    result = compose_freshness([FreshnessPolicy(3600), expired])
    assert result is not None
    assert result.max_age_seconds == 3600
    assert result.is_expired()
