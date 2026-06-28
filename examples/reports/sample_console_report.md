# Sample console report

```text
ACDM Validation Report
Status: FAILED
Entities checked: 3
Findings: 9 errors, 0 warnings
Maturity level: 1

[ERROR] R1 customer_risk_view.trust_tier
Declared trust tier is better than the weakest dependency trust tier.
Fix: Change trust_tier to T3 or provide a documented certified_upgrade.

[ERROR] R3 customer_risk_view.provenance_binding
Missing contributing sources: vendor_fraud_api.
Fix: Add every contributing source to provenance_binding.

[ERROR] R6 customer_risk_view.allowed_agent_actions
Declared action 'decide' exceeds the computed permission ceiling 'summarize'.
Fix: Remove actions above summarize or correct the governing properties.
```

The complete failing example also reports R2, R4, R5, R8, R9, and R10.

