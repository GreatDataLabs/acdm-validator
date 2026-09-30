# ACDM Validator

**Design-Time Contract Validation for Agent Contract Data Modeling**

> Make ACDM enforceable by validating entity contracts, composition rules, permission ceilings, and
> maturity levels in CI.

## ACDM resources

- **ACDM overview:** <https://greatdatalabs.github.io/acdm/>
- **White paper PDF:** <https://greatdatalabs.github.io/assets/acdm/acdm-white-paper-final.pdf>
- **GreatDataLabs organization:** <https://github.com/GreatDataLabs>

ACDM Validator makes Agent Contract Data Modeling enforceable. It reads Entity Contracts, checks
them against ACDM composition rules and the permission model, assigns maturity levels, and emits
audit records that can be used in CI/CD governance workflows.

ACDM Validator operationalizes Agent Contract Data Modeling by checking whether declared entity
contracts are complete, composition-consistent, permission-consistent, and maturity-aligned.

## Why a validator?

Governance prose does not fail a build. A declared trust tier can improve across a join, provenance
can disappear, or an agent permission can exceed the weakest input without an automated signal.
This library turns those design-time assertions into deterministic findings and a process exit code.

- **ACDM** is the methodology.
- **Entity Contracts** are its design-time governance artifacts.
- **ACDM Validator** is the reference implementation that validates those artifacts.

It is suitable for CI/CD, design reviews, data-product governance, and agent-readiness checks.

## Installation

```bash
python -m pip install acdm-validator
```

Python 3.10 or newer is required. The only runtime dependency is PyYAML.

## Quickstart

```bash
acdm-validate ./contracts/
```

```yaml
entity_name: customer_risk_view
business_definition: "A derived view supporting customer risk recommendations."
primary_keys: [customer_id]
depends_on: [member_profile, vendor_fraud_score]
trust_tier: T3
freshness_policy: {max_age: "12h"}
provenance_binding: [member_db, vendor_fraud_api]
cost_class: C2
risk_class: R3
allowed_agent_actions: [read, summarize, recommend]
human_approval_required: true
downstream_exposure_rules: {mask: [ssn, dob]}
owner: data-risk-team
review_frequency: "30d"
certified_upgrade: null
```

The loader accepts a single `.yml`/`.yaml` file or recursively discovers contracts in a directory.

## Example failure

```text
ACDM Validation Report
Status: FAILED
Entities checked: 3
Findings: 9 errors, 0 warnings
Maturity level: 1

[ERROR] R1 customer_risk_view.trust_tier
Declared trust tier is better than the weakest dependency trust tier.
Fix: Change trust_tier to T3 or provide a documented certified_upgrade.
```

Try both curated examples:

```bash
acdm-validate examples/contracts/clean_join/
acdm-validate examples/contracts/failing_join/  # intentionally exits 1
```

## CLI

```bash
acdm-validate ./contracts/
acdm-validate ./contracts/ --format json
acdm-validate ./contracts/ --fail-on L2
acdm-validate ./contracts/ --output report.json
acdm-validate ./contracts/ --audit-output audit.json
```

Exit `0` means the configured policy passed, `1` means findings crossed the threshold, and `2`
means contracts could not be loaded or the command was invalid. The default fails on errors.
`--fail-on warning` also fails on warnings. `L1`, `L2`, and `L3` enable errors through that validation
stage, so `L2` considers L1 completeness and L2 composition errors.

## Python API

```python
from acdm_validator import validate_contracts

report = validate_contracts("./contracts")
print(report.status)
print(report.findings)
print(report.data_product_maturity)
```

The same engine can validate already-loaded objects:

```python
from acdm_validator import load_contracts, validate

contracts = load_contracts("./contracts")
report = validate(contracts)
assert report.status == "passed"
```

## Composition rules

| Rule | Invariant |
|---|---|
| R1 | Trust cannot improve beyond the weakest input without documented certification. |
| R2 | Freshness cannot be looser than the strictest dependency requirement. |
| R3 | Provenance includes every contributing source. |
| R4 | Cost classes and numeric budgets accumulate. |
| R5 | Risk cannot decrease below the highest-risk input. |
| R6 | Declared actions do not exceed the composed permission ceiling. |
| R7 | Expired inputs make derivatives expired until refresh. |
| R8 | Masking and exposure constraints propagate. |
| R9 | Upgrades beyond computed defaults require documentation. |
| R10 | Composition conflicts become findings rather than silent coercions. |

Resolved output remains conservative even when a declaration violates a rule. That prevents one bad
contract from granting downstream entities a more favorable computed property.

## Permission model

Actions form an ordered ladder:

```text
none < read < summarize < recommend < decide < act
```

The default matrix considers resolved trust, freshness, risk, provenance, cost, approval, masks, and
the strictest dependency ceiling. T4 caps at `read`; expired or missing-provenance entities cap at
`summarize`; R3 requires approval to reach `recommend`; R4 blocks `decide` and `act`; high cost is a
constraint, never a grant. The complete matrix is in [docs/permission-model.md](docs/permission-model.md).

## Maturity model

| Level | Meaning |
|---:|---|
| 0 | No valid contract (L1 errors). |
| 1 | Complete, but derived composition has errors. |
| 2 | Composition-consistent, but permission checks have errors. |
| 3 | Permission-consistent. |
| 4 | Certified with documentation and a review within `review_frequency`. |

Data-product maturity is the minimum entity maturity, intentionally preserving the weakest link.

## Reports and audit records

Console output is optimized for reviews. JSON includes `status`, `entities_checked`, findings,
per-entity maturity, product maturity, resolved properties, and `generated_at`. Audit records add the
validator version and dependency composition. Python helpers can optionally project an OpenLineage
facet and OpenTelemetry attributes; they do not send telemetry or modify a lineage service.

## CI/CD

```yaml
- run: python -m pip install acdm-validator
- run: acdm-validate contracts/ --format json --output acdm-report.json
```

The included GitHub Actions workflow tests Python 3.10-3.13 and validates the clean join. See
[docs/ci-cd-usage.md](docs/ci-cd-usage.md) for GitHub Actions and Azure DevOps examples.

## Relationship to the ACDM whitepaper

The whitepaper defines the methodology and governance semantics. This repository is a small,
testable reference implementation of its Entity Contract checks. It does not claim to invent
provenance, lineage, trust propagation, or runtime AI governance. Rule interpretations are explicit
in [SPEC.md](SPEC.md) so teams can review where policy becomes code.

## Deliberately out of scope

This is not a runtime agent enforcement engine, lineage system, data catalog, access-control system,
trust-score generator, risk-scoring model, provenance theory, or live data-quality engine. Owners
declare governance properties; the validator checks their consistency after dependency composition.
It never gates live agent calls or computes trust and risk from raw records.

## Roadmap

- **Tier 0:** YAML, property types, dependency graph, R1-R5/R7, reports, CLI, tests.
- **Tier 1 (this release):** R6/R8-R10, permission matrix, maturity 3/4, JSON and audits.
- **Tier 2:** dbt and catalog adapters, richer OpenLineage/OTel integrations, reusable pipeline tasks.

See [docs/roadmap.md](docs/roadmap.md). The project should not be cited as a paper implementation
before a Tier 1 release is runnable.

## Contributing

Install development dependencies with `python -m pip install -e ".[dev]"`, then run `ruff check .`
and `pytest`. Behavioral changes need tests and a written explanation of their governance semantics.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
