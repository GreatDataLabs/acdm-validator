# Entity Contracts

Contracts are UTF-8 YAML mappings. All thirteen core fields are required. `depends_on` contains
entity names, not filenames, and therefore names must be unique within a validation run. Directories
are scanned recursively.

Freshness accepts `{max_age: "24h", as_of: "2026-06-28T12:00:00Z", expired: false}`. Cost accepts a
class string or `{class: C2, budget: 50}`. Certification should be a mapping such as:

```yaml
certified_upgrade:
  reference: GOV-142
  reason: "Reviewed transformation control"
  reviewed_at: "2026-06-20T00:00:00Z"
```

Certification does not suppress provenance and masking from resolved audit output; those remain
visible so downstream reviewers can see the full contributing constraint set.

