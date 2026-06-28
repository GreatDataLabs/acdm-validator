# Permission model

The default action order is `none`, `read`, `summarize`, `recommend`, `decide`, `act`. The engine
first derives a local ceiling from resolved properties, then takes the minimum local/dependency
ceiling. A contract may declare any subset below that ceiling; it cannot use cost or approval as a
grant above constraints imposed elsewhere.

| Condition | Cap |
|---|---|
| Missing typed trust, risk, or freshness | none |
| T4 | read |
| T3 without approval | summarize |
| T3 with approval | recommend |
| T1 and R1 | decide |
| T1/T2 otherwise | recommend |
| R3/R4 without approval | summarize |
| R3/R4 with approval | recommend |
| Expired, missing provenance, or C4 | summarize |
| Propagated masks | recommend |

The matrix is conservative and code-defined in version 0.1.0. A future policy adapter will make it
configurable without changing contract parsing or findings.

