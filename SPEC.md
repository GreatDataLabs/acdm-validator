# ACDM Validator Engineering Specification

## 1. Purpose and scope

ACDM Validator is a design-time validator for YAML Agent Contract Data Modeling Entity Contracts. It
normalizes declared properties, composes dependency constraints, checks named rules, computes an
agent-action ceiling, assigns maturity, and emits deterministic reports and audit records. CLI and
Python API calls use the same engine.

It validates declarations. It does not inspect underlying records, generate trust or risk scores,
enforce live requests, replace authorization, discover lineage, or publish telemetry.

## 2. Contract schema

Every contract requires thirteen fields: `entity_name`, `business_definition`, `primary_keys`,
`trust_tier`, `freshness_policy`, `provenance_binding`, `cost_class`, `risk_class`,
`allowed_agent_actions`, `human_approval_required`, `downstream_exposure_rules`, `owner`, and
`review_frequency`. `depends_on` marks a derived entity. `certified_upgrade` optionally contains an
upgrade reference and may include `reviewed_at`.

Trust is T1-T4 and risk is R1-R4, with increasing rank representing weaker trust or higher risk.
Freshness requires `max_age` (`s`, `m`, `h`, `d`, or `w`), and may declare `as_of` and `expired`.
Provenance is a non-empty set of source IDs. Cost accepts `C1`-`C4` or
`{class: C2, budget: 100}`. Actions come from the ordered ladder. Exposure is a mapping whose
`mask` key is a list of field names.

Malformed required fields become `SCHEMA`/L1 findings instead of terminating validation. Invalid
YAML, non-mapping documents, unsupported file extensions, and empty directories are load errors.

## 3. Object model and graph

`EntityContract` preserves source and raw data while exposing normalized typed properties.
`TrustTier`, `RiskClass`, `FreshnessPolicy`, and `Cost` encapsulate parsing and rank semantics.
`DependencyGraph` identifies duplicate entities, missing inputs, and cycles, and supplies a stable
dependency-first order. Graph-invalid entities do not receive cascading composition findings.

`ResolvedProperties` is the conservative result used downstream. An uncertified favorable
declaration never improves resolved trust, risk, or freshness. Provenance and masks are always
unioned, and understated costs resolve to computed costs.

## 4. Composition algorithms

- Trust: maximum rank (weakest/deepest tier).
- Freshness: minimum `max_age`; oldest `as_of`; expiration is logical OR.
- Provenance: set union.
- Cost: sum ranks capped at C4; sum budgets when every input supplies a budget.
- Risk: maximum rank.
- Masks: set union.
- Permission: minimum of the local computed ceiling and all dependency ceilings.

## 5. Rules and validation levels

L1 checks schema completeness, enums, durations, actions, ownership, keys, definition, and review
frequency. L2 checks graph and R1-R5/R7-R8. L3 checks R6/R9/R10.

| ID | Check | Default fix |
|---|---|---|
| R1 | Declared trust is not better than composed trust. | Use computed tier or document certification. |
| R2 | Declared max age is not looser than the strictest input. | Tighten max age or certify. |
| R3 | Declared provenance contains the composed union. | Add missing sources. |
| R4 | Declared cost covers accumulated rank/budget. | Raise class or budget. |
| R5 | Declared risk is not below composed risk. | Raise risk or certify. |
| R6 | Every declared action is at or below the ceiling. | Remove excessive actions. |
| R7 | Dependency expiry propagates. | Refresh or declare expiry. |
| R8 | Dependency masks propagate. | Preserve masks or certify. |
| R9 | Favorable property upgrades have durable documentation. | Add reference or remove upgrade. |
| R10 | Declared permissions conflicting with composition are explicit. | Align permission and inputs. |

## 6. Permission ceiling

The ladder is `none < read < summarize < recommend < decide < act`. Missing required normalized
governance properties yield `none`. T4 caps at `read`; T3 normally caps at `summarize`, reaching
`recommend` only with human approval. T1/R1 can reach `decide`; other T1/T2 combinations reach
`recommend`. R3/R4 without approval cap at `summarize`; with approval they cap at `recommend`.
Expired data, missing provenance, and C4 cost cap at `summarize`. Masks cap unrestricted behavior at
`recommend`. Nothing in cost can raise a ceiling. Dependency ceilings are composed by minimum.

This matrix is a reference default, not a claim that one policy fits every organization. Future
versions may accept a versioned policy configuration.

## 7. Maturity

Entity maturity is 0 with L1 errors, 1 with unresolved L2 errors, 2 with L3 errors, and 3 when all
permission checks pass. Level 4 additionally requires documented certification metadata with a
parseable `reviewed_at` timestamp no older than `review_frequency`. Product maturity is the minimum
entity score. This prevents averages from hiding a weak entity.

## 8. Findings and outputs

Each finding contains `rule_id`, `level`, `severity`, `entity`, `field`, `message`,
`declared_value`, `computed_value`, `dependencies`, and `recommended_fix`. JSON reports contain
status, counts, findings, maturity, resolved properties, and an RFC 3339 UTC generation time.

Audit records add validator name/version, dependency composition, and validation time. Optional
helpers return an OpenLineage-compatible custom facet or OpenTelemetry attribute mapping. Emission
is side-effect free unless the caller explicitly writes the returned record.

## 9. CLI contract

`acdm-validate PATH` renders console output. `--format json`, `--output`, and `--audit-output` control
artifacts. Default `--fail-on error` fails for any error; `warning` includes warnings; L1-L3 include
error findings through the selected validation stage. Exit codes are 0 pass, 1 policy failure, and 2
load/usage failure. Files are written as UTF-8 and JSON is stable-key, two-space indented.

## 10. Versioned delivery plan

Tier 0 is the usable YAML/composition core. Tier 1 adds permission and audit alignment and is the
minimum release suitable for reference from the ACDM paper. Tier 2 adds adapters for dbt metadata,
Unity Catalog and generic catalog tags, JSON/registry inputs, expanded OpenLineage and OpenTelemetry
integration, and packaged GitHub/Azure pipeline components. Adapters must produce `EntityContract`
objects and must not fork rule semantics.

