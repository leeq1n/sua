# Mechanism-space search evaluation plan

> L0: Candidate AI4S evaluation plan for reducing rediscovery and identifying a testable mechanism delta.
> Status: design baseline only; no measured behavioral effect or validated algorithm.
> Load when: evaluating large-space scientific search after the current Authority/Science story gate.
> Last P20-verified: 2026-09-27

## Goal and boundary

Test whether a mechanism-family search policy, under the same call and time
budget, reduces rediscovery and finds valid distinct mechanisms sooner than
existing SUA K2-K5 guidance. A different name, embedding position, or larger
candidate count is not success. This is an AI4S project-layer research question;
it does not mutate the general SUA control plane or add a principle.

The Authority/Science benchmark and its story-selection decision remain a
separate active study. Do not reinterpret its results as evidence for this
search-policy question. Begin this study only after that gate is resolved or
explicitly scheduled as a parallel, separately measured project.

## Candidate baseline surface

`../../benchmarks/mechanism_space_v0.json` contains eight unmeasured regression
cases. It covers renamed duplicates, cross-domain uncertainty, false merging
from shared words, missing discriminators, family saturation, novelty proxies,
minimal-delta extraction, and goal drift. Expected decisions and rubrics are
evaluation keys, not prompt content. Structural tests prove only fixture shape.

Before a model comparison, add independently authored held-out cases from
multiple domains and freeze their evidence-backed mechanism relations. At least
one case must allow more than one valid surviving kernel; at least one must
require `UNCERTAIN`. Keep source and gold rationale separate from model inputs.
The evaluator must be independent of the policy author under P30.

## Candidate mechanism-space representation

For each proposal, retain: mother problem, failed assumption, necessary
constraint, claimed causal mechanism, predicted observable, cheapest falsifier,
nearest known mechanism, precise delta, evidence sources, and current K-state.
Keep stable IDs and versioned links to prior candidates and negative knowledge.

Retrieval proposes comparison pairs. A comparison can be `SAME`, `DIFFERENT`,
or `UNCERTAIN`, with a supporting causal witness or discriminating observation.
Do not permanently merge on embedding similarity or an unsupported LLM label.
Conflicting evidence must reopen the relation without deleting its history.

## Search policy to test

1. Construct a bounded set of distinct failed assumptions and mechanism
   hypotheses before terminal reduction, per Add-then-Reduce.
2. Check the ledger and nearest mature mechanisms; stop local variants when
   they reproduce a recorded family with no reopening evidence.
3. Choose the next search or cheap test by the decision it can change and its
   cost. Explore uncovered mechanism boundaries; trigger LIFT/RESET when a
   family or mother space saturates. Record the budget and stop reason.
4. For each survivor, remove superficial features and compare the smallest
   remaining causal delta with the strongest prior. Hold multiple kernels or
   `UNKNOWN` when evidence cannot discriminate. K4 does not imply K5/K6.

This is a policy hypothesis, not an algorithmic guarantee. Any information-gain
or diversity heuristic is an experimental component whose assumptions and
failure cases must be measured.

## Measurement and gates

Compare equal-budget arms: random candidate selection, semantic deduplication,
diversity-only selection, current SUA K2-K5 guidance, and the candidate policy.
Freeze the prompts, corpus snapshot, retrieval access, model identity, budget,
scorer, and stopping rule before observing outcomes. Preserve actual calls,
tokens, wall time, retrieved sources, candidate IDs, and decisions.

Primary outcomes: verified rediscovery rate; cost to first valid distinct
mechanism; and correct identification of a minimal mechanism delta. Safety
outcomes: false merges of distinct mechanisms, unsupported novelty claims,
invalid reopening, and failure to abstain. Report each separately by failure
mode; do not hide high-cost false merges in an average score. Gold novelty
requires K3/K4 evidence, and claimed causal value needs a K5 falsifier.

Advance from baseline design to policy implementation only after fixture and
scoring validity review. Promote any behavior to default AI4S guidance only
after held-out, equal-budget evidence and independent acceptance. If the
candidate does not improve the primary outcomes without unacceptable false
merges, retain the negative result and remove the added policy complexity.

## Applicable rules

- P5/P18: freeze measurable failures before implementation and regress them.
- P7/P11/P20: reuse AI4S K2-K5 and existing knowledge ledgers; keep this
  conditional plan outside the default context path.
- P17/P30: distinguish structural checks, measured behavior, and independent
  acceptance.
- P22/P29: stop repeated local search and preserve only decision-relevant
  context.
