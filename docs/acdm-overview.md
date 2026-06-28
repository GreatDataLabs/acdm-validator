# ACDM overview

Agent Contract Data Modeling treats an entity's governance properties as a reviewable interface.
The methodology defines the semantics; Entity Contracts record owner declarations; this validator
checks those declarations before deployment. It is most useful at design-review and CI boundaries,
where an actionable finding can prevent an inconsistent contract from becoming a data dependency.

The validator is intentionally declarative. It does not infer whether a source deserves T1 or R3.
It verifies that a derivative cannot quietly claim stronger properties or broader permissions than
its inputs support.

