# Composition rules

Dependency properties are resolved before their consumer. Trust and risk use worst-case ranks,
freshness uses the shortest age and propagates expiry, provenance and masks use set union, and cost
adds conservatively. A derived declaration is compared with those results under R1-R5, R7, and R8.

Violations create findings and retain conservative resolved values. This detail matters in a chain:
an invalid intermediate T1 declaration over a T3 input still behaves as T3 when its consumer is
validated. Documented certification permits favorable trust, risk, or freshness upgrades, while the
audit record continues to expose composed sources and constraints.

