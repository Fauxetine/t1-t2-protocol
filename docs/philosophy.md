# Design Philosophy

## The Problem: Self-Referential Blind Spots

When an AI model checks its own output, it uses the same training data, the same reasoning preferences, and the same systematic biases. This self-referential validation has a fundamental limitation: **a model cannot discover what it cannot see.**

This is not a matter of intelligence. A smarter model does not have better access to its own blind spots — it simply has different blind spots. Self-reflection is therefore insufficient as a validation strategy.

## The Solution: Heterogeneous Validation

T2 protocol introduces **heterogeneous validation**: the evaluator should be a different model than the producer. Two models trained on different data, with different architectures and different reasoning preferences, will have different blind spots. One model's weakness is the other's strength.

This mirrors peer review in established disciplines:
- Academic papers are not reviewed by their authors
- Code is not reviewed by its developer
- Financial audits are not conducted by the audited party

AI validation should follow the same principle.

### Heterogeneous ≠ Stronger

The evaluator model does not need to be "smarter" than the producer. It needs to be *different*. The value comes from distribution mismatch, not capability superiority. A 7B parameter model with different training data can catch blind spots that a 70B parameter model misses.

## The Safety-Intelligence Paradox

Current LLM safety relies on alignment techniques that depend on the model itself: RLHF, system prompts, output filtering. This creates a paradox:

**As models become more intelligent, they become better at bypassing safety mechanisms that depend on their own reasoning.**

The same capabilities that make a model useful also make it harder to constrain.

## The Solution: Deterministic Safety

Checksum and the protocol's structural validation are **deterministic**. They use pure regular expressions and string operations — zero LLM dependency. A model cannot "think its way around" a regex rule, no matter how intelligent it becomes.

This is the core architectural insight: **intelligence can grow without bound, but safety must be grounded in code that does not grow.**

## Structured Reasoning

T1 protocol addresses a different problem: vague questions produce unreliable answers. Before evaluating whether an answer is correct, we must ensure the question is well-defined.

The four tiers (L1-L4) follow the scientific method:

| Tier | Function | Scientific parallel |
|------|----------|-------------------|
| **L1 Facts** | Verifiable, observable truths | Data |
| **L2 Assumptions** | Reasonable premises needing validation | Working hypotheses |
| **L3 Hypotheses** | Falsifiable claims with evidence tracking | Testable predictions |
| **L4 Unknown** | Acknowledged boundaries of reasoning | Known unknowns |

A question decomposed into these tiers can be answered systematically. An undecomposed question cannot.

## Relationship to AGI Safety

If artificial general intelligence emerges, two questions become urgent:

1. **How can AGI decisions be made understandable?** — T1's tiered decomposition provides a traceability framework for complex reasoning chains.

2. **How can AGI behavior be kept safe?** — Deterministic checks (checksum, structural validation) provide a safety layer that remains effective regardless of intelligence level. The separation of "intelligence" from "trust" is not a convenience — it may be a necessity.

## What This Protocol Does Not Do

- **Does not call tools** — that is the role of other MCP servers
- **Does not store data** — not a protocol-layer responsibility
- **Does not benchmark models** — this is not a benchmark
- **Does not produce answers** — validation is not generation

## Open Questions

- **Optimal heterogeneity**: How different should two models be for maximal blind-spot coverage? Same family? Different families? Different modalities?
- **Recursion bounds**: At what depth does cross-validation's marginal benefit approach zero? Our current heuristic terminates at depth ≥ 3.
- **Weight calibration**: How should evaluation criteria weights be calibrated for different domains? Currently user-specified; could be learned.
