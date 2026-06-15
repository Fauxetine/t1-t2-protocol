# Full Pipeline: T1 → Decision → T2

Demonstrates the complete heterogeneous validation workflow.

## Step 1: T1 — Structure the question

```
Call: t1_protocol("Evaluate microservices migration")
  → Returns L1/L2/L3/L4 structured prompt
```

## Step 2: Make a decision based on structured info

```
"Pilot with 1-2 services first. Validate service boundaries and team capability.
If successful within 3 months, migrate remaining services incrementally."
```

## Step 3: T2 — Cross-validate the decision

```
Call: t2_protocol(decision text)
  → Returns:

Confidence: Medium-High
  - Pilot strategy is low-risk and reasonable
  - Recommendation: add quantitative success criteria

| Adopt | Content | Correction | Evidence |
|-------|---------|------------|----------|
| ✅ | Pilot migration strategy | — | L1 |
| ✅ | 3-month evaluation window | — | L2 |
| ⚠️ | "Successful" not defined | Add metrics (deployment frequency + X%, error rate not increasing) | L2 |
```

## The value chain

```
Vague question → T1 structural decomposition → Decision based on facts, not intuition
Decision → T2 heterogeneous validation → Blind spots discovered and corrected
Corrected decision → Execution → More reliable outcome
```

This is the complete T1/T2 collaboration workflow.
