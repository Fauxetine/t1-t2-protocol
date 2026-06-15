# T1 Example: Structuring a Vague Question

## Scenario

You're evaluating whether to adopt a new architecture approach, but the question is too vague for a reliable answer.

## Input

Call `t1_protocol` with:

```
Evaluate the feasibility of migrating from a monolith to microservices
```

## Output

```
[L1 Facts]
1. Current app is a monolith with ~500K lines of code
2. Team has 5 developers
3. Deployment cycle is bi-weekly
4. Current stack: Python/Django

[L2 Assumptions]
1. Microservices will improve deployment frequency (needs verification)
2. Team can maintain a distributed system (needs verification)
3. Business logic can be cleanly split into services (needs verification)

[L3 Hypotheses]
1. Microservices reduce deployment risk per change
   ├─ Evidence: Indirect support from industry cases
   └─ Debate: complexity shifts from deployment to operations
2. Migration won't impact existing business
   ├─ Evidence: Theoretical only
   └─ Debate: incremental vs rewrite approach

[L4 Unknown]
1. Future business growth trajectory
2. Team's distributed systems learning curve

[Core Question]
Given 5-person team and Python/Django constraints,
does microservices deployment flexibility justify the distributed complexity cost?
```

## Value

- Converts a vague "is it good?" question into a structured, debatable problem
- Separates known facts from assumptions requiring verification
- Surfaces the key debates that need investigation
