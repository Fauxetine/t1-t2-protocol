# T2 Example: Cross-Validating a Decision

## Scenario

You've made a decision and want another model to examine it for blind spots.

## Input

Call `t2_protocol` with:

```
I've decided to adopt microservices:
1. Improve deployment frequency
2. Teams can develop independently
3. Technology stack can be diversified
```

## Output

```
Confidence: Medium-Low
  - Description: Direction is reasonable, but key constraints lack verification
  - Recursion depth: Layer 0
  - Weight assumption: Fact-first

Adoption Recommendations:

| Adopt | Content | Correction | Evidence |
|-------|---------|------------|----------|
| ✅ Adopt | Microservices improve deployment frequency | — | L1 |
| ⚠️ Reserved | Teams develop independently | Verify service boundary clarity first | L2 |
| ⚠️ Reserved | Stack diversification | 5-person team may struggle with diverse stacks | L2 |
| ❌ N/A | Distributed complexity not addressed | Add operations and monitoring plan | L2 |
```

## Value

- Discovers blind spots that self-reflection would miss
- Labels confidence by evidence tier (L1 = verified, L2 = needs work)
- Provides actionable corrections, not just criticism
