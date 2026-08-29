# AI4S Research Mode — operating detail

> L0: L2 protocol for scientific-state transitions, epistemic triggers,
> evidence gates, novelty review, and negative knowledge.

## 1. What the controller controls

The controller acts on **scientific knowledge state**, not software delivery
phase. K0-K7 answer what is currently known, what is claimed, and what
evidence permits the next claim. Planning, coding, experiments, and writing
may occur inside several states; none of them proves a state transition.

The canonical operations remain in SUA:

- Analyze and Reason frame the object and causal structure.
- Association/analogy searches neighboring mechanisms.
- Induction summarizes repeated collisions and lifts abstraction.
- Critical primitives run challenge, inversion, pre-mortem, and the strongest
  opposing argument.
- M-add-then-reduce consolidates or destroys branches that no longer earn
  complexity.
- P5/P17 verification and honest status govern evidence claims.
- P22/P28/P29 govern replanning, self-application, and active reduction.

This adapter only decides **when** those operations fire and which transitions
they may block.

## 2. State transitions

| From | Advance condition | Failure route |
|---|---|---|
| K0 -> K1 | Mother problem, scientific object, target claim, and excluded optimization are explicit. | HOLD K0; reframe rather than brainstorm attacks or applications. |
| K1 -> K2 | A verified capability change invalidates an identifiable old assumption under a necessary constraint. | HOLD K1; frontier scan or RESET mother space. |
| K2 -> K3 | `Capability -> Broken Assumption -> Mechanism` representation and cheap falsifier are specific. | REDUCE assumptions or return K0/K1. |
| K3 -> K4 | Generic mechanism is stable and mechanism-level adjacent theory coverage reaches the stopping condition. | Continue targeted search; LIFT if local vocabulary keeps colliding. |
| K4 -> K5 | Prosecutor and Reviewer #2 fail to eliminate a precise Author mechanism delta. | KILL, REDUCE, LIFT, or RESET; write ledger entry. |
| K5 -> K6 | Cheapest decisive falsifier fails to kill the candidate and bounds the surviving claim. | KILL or return K2; do not rescue with an expensive MVP. |
| K6 -> K7 | Claim-matched native/external evidence survives adapter and natural-failure controls. | Downgrade claim, redesign validation, or KILL. |

K7 is not permanent truth. Strong counterevidence reopens the relevant prior
state and updates the ledger rather than erasing the earlier decision.

## 3. Epistemic triggers

Triggers fire from observed evidence, independent of user wording.

### Repeated mechanism collision

When two or more nearby candidates in one branch are rejected by the same
generic prior-art mechanism, STOP local generation. Induct the shared failure,
then choose LIFT to a higher scientific object or RESET to a different mother
space. A third renamed variant requires new evidence that changes the generic
mechanism.

### Combination-only novelty

If the claim decomposes into known A + known B + known C, ask what causal,
informational, strategic, or computational mechanism exists only because of
their interaction. If no testable interaction mechanism remains after
removing the application labels, KILL or Reduce at K4.

### Renaming without mechanism change

A changed domain, modality, terminology, model family, deployment location,
or adversary name is not a mechanism delta. Route to K3 and search the generic
mechanism; do not let vocabulary novelty advance K4.

### Adapter dependence

If an effect depends on custom measurement, projection, controller, proxy, or
non-native simulation assumptions, block native-system and external-validity
claims. At K6 compare native-only, adapter-only, and matched-control paths;
identify which component creates the effect.

### No cheap falsifier

If no affordable observation could kill or sharply bound the mechanism, it is
not mature enough for novelty review. Return to K0-K2. A large MVP is not a
substitute for a falsifiable claim.

### Claim/evidence mismatch

Block progression when the evidence class cannot support the claim type:
keywords for novelty, correlation for causality, toy simulation for native
validity, or ordinary reliability failure for security advantage. Downgrade
the claim or obtain claim-matched evidence.

### Candidate rescue inflation

When every failed review adds an assumption, attacker ability, component,
metric, or domain exception, freeze additions and run M-add-then-reduce. Keep
only the minimum mechanism that survives independently; otherwise KILL.

### Mother-space saturation

When a family repeatedly maps to mature adjacent theories, stop producing
variants. Summarize the saturation evidence, persist it in the ledger, and
RESET to a different scientific object. More names are not more entropy.

## 4. Candidate gate: Capability -> Broken Assumption -> Mechanism

Before K4, every strong candidate must state:

```text
NEW CAPABILITY: What recently became possible, with evidence?
OLD ASSUMPTION: What did prior systems or theory rely on?
NECESSARY CONSTRAINT: Why must that assumption now fail?
NEW MECHANISM: What property or interaction is not already captured?
CHEAP FALSIFIER: What inexpensive result would kill or sharply bound it?
```

The representation is a maturity gate, not proof of novelty. If the NEW
MECHANISM merely restates the application, move back to K2.

## 5. Cross-domain analogy scheduler

Before K4, search by mechanism, not by nouns. Remove domain names and build
the strongest generic formulation: variables, causal arrows, information
boundaries, strategic timing, observability, verification property, and cost
model. Then schedule SUA's canonical analogy operation across fields that
study the same structure, including non-security and non-application theory.

Examples of bridge shape, not a fixed checklist:

```text
partitioned evidence -> distributed verification -> zero knowledge / MPC
protocol ambiguity -> parser differential -> language-theoretic security
delegated AI decision -> information-flow control -> runtime assurance
```

Stop when all of the following hold:

1. the generic mechanism no longer changes under new terminology;
2. the nearest mature theory families and their strongest counterexamples
   have been examined;
3. new searches mostly duplicate already classified mechanisms; and
4. Prosecutor can explain why remaining work is DIFFERENT rather than merely
   failing to find a matching noun.

Coverage is recorded as mechanism -> field -> strongest work -> relation ->
uncovered delta. No fixed domain count is required.

## 6. Sequential novelty tribunal

Use sequential roles by default; do not introduce multi-agent orchestration in
Phase A.

1. **Prosecutor** receives the largest search and counterevidence budget. Its
   goal is to prove the candidate known, construct the strongest generic
   mechanism, and locate mature theory that already supplies the property.
2. **Reviewer #2** removes application labels such as satellite, robot, or
   model family. It asks whether the scientific object remains new and
   whether the proposal changes a property, an interaction, or only cost.
3. **Author** acts last. It may state only the exact mechanism delta surviving
   both attacks. It cannot rescue novelty with terminology, implementation
   difficulty, operational cost, or extra assumptions.

Classify each prior work using the existing-compatible minimal relation set:

- `EXACT`: same object, mechanism, and material claim.
- `MECHANISM_EQUIVALENT`: same causal/property mechanism under other names.
- `HIGHLY_ADJACENT`: nearest mechanism differs at a stated boundary.
- `FOUNDATIONAL`: supplies the general theory or primitive.
- `DIFFERENT`: lacks the necessary mechanism after explicit comparison.

The K4 decision is `KILL`, `REDUCE`, `LIFT`, `RESET`, or
`PROVISIONALLY_RETAIN`. Only the last enters K5.

## 7. Claim type and evidence gates

Use the smallest claim type that matches the sentence. Mixed claims must pass
every applicable row.

| Claim type | Acceptable evidence | Insufficient evidence | Transition gate |
|---|---|---|---|
| Capability / feasibility | Current system, dataset, instrument, API, or reproducible access evidence | Announcement, stale plan, or assumed availability | K1 may advance only after availability and constraints are verified. |
| Literature | Primary source supports the attributed statement | Search snippet, uncited summary, or neighboring paper | Record source and scope before using it in K3/K4. |
| Novelty | Mechanism-level search, bridge coverage, and tribunal delta | Keyword absence or new application noun | Prosecutor + Reviewer #2 completed at K4. |
| Causal | Intervention, counterfactual, ablation, or identification argument | Correlation or a single positive curve | Cheap falsifier at K5; confounds explicitly bounded. |
| Security | Attacker advantage over matched natural failure under a stated threat model | Reliability degradation with no adversarial advantage | Matched control and attacker capability at K6. |
| External validity | Native target-system evidence across relevant conditions | Toy simulation or adapter-created proxy alone | Native/adapter audit at K6. |
| Theoretical | Defined object, assumptions, property, and proof or valid derivation | Analogy or notation without a new theorem/property | Surviving K4 object and explicit assumptions before K7. |

Feasibility does not imply novelty; novelty does not imply causality; toy causal
identification does not imply external validity.

## 8. Negative scientific knowledge ledger

Every KILL, REDUCE, LIFT, or RESET writes or updates a durable project ledger.
Projects choose the ledger path; SUA defines only the schema and operating
contract. Satellite examples remain benchmark fixtures, not SUA product
knowledge.

```yaml
id:
claim:
scientific_object:
capability_delta:
broken_assumption:
necessary_constraint:
mechanism:
closest_prior_art:
mechanism_equivalent_work:
strongest_counterevidence:
cheap_falsifier:
kill_condition:
status: KILLED | REDUCED | LIFTED | RESET | OPEN
do_not_revive_unless:
```

Before opening a candidate, search ledger entries by generic mechanism and
broken assumption. A renamed candidate inherits the prior status unless it
satisfies `do_not_revive_unless` with new evidence. Reopening appends the new
evidence and decision; it does not delete the negative result.

## 9. Frontier capability radar

K1 begins from verified changes more often than attack brainstorming. Perform
a lightweight, task-bounded scan of recent papers, preprints, mission/system
reports, datasets, hardware, standards, APIs, and instruments. For each real
change ask which former assumption it invalidates, under what necessary
constraint, and which scientific property may change.

Phase A does not build a crawler. Stop when the relevant capability classes
are represented, sources begin repeating, and unresolved availability claims
are marked rather than guessed.

## 10. Cheap falsification resource policy

Rank proposed checks qualitatively by **expected kill value / cost**. Run the
cheapest decisive falsifier before the most impressive experiment; do not
invent unsupported probabilities. The default resource order is:

1. mechanism decomposition and strongest generic counterexample;
2. prior-art tribunal;
3. minimal analytic, toy, or ablation falsifier;
4. native single-case validation;
5. population-scale or expensive implementation.

Exceptions require an explicit non-novelty objective or evidence that the
cheaper check cannot discriminate the claim.

## 11. Benchmark and decision contract

The `ai4s_regression` entries in `benchmarks/tasks.json` encode six synthetic
failure patterns. The same prompts are evaluated against baseline
`RESEARCH_USAGE.md` and treatment AI4S Research Mode. Each fixture contains a
transparent criterion list; ratings are human or explicitly judge-assisted,
never described as deterministic. Deterministic tests verify fixture coverage,
routing, schema, and progressive disclosure only.

The suite measures state identification, spontaneous cross-domain search,
mechanism-equivalent detection, Reduce, combination blocking, native audit,
KILL persistence, MVP blocking, and lift/reset. Also record unnecessary tool
or role calls. A single model/run is directional evidence, not a general
effect estimate.

Phase A's AI4S adapter outcomes are:

- `AI4S_PROJECT_ADAPTER_VALIDATED`: project routing plus tests are discoverable and
  treatment evidence improves the target behaviors without core edits.
- `AI4S_ADAPTER_FAILED`: the controller cannot improve behavior without a
  rewrite larger than the problem.

Generic specialization uses the separate outcomes in
`DOMAIN_SPECIALIZATION_BOOTSTRAP.md`; adapter success is not evidence for
`DOMAIN_SPECIALIZATION_BOOTSTRAP_VALIDATED`. A core trigger remains proposal-
only if project routing repeatedly fails fresh-agent activation.

For Phase A: Do not modify `core-layer/`, hooks, or established P-n. Any core
trigger is proposal-only and requires separate authorization.

## 12. Self-application and pre-mortem

Before accepting this controller, attack it as follows:

- If it is merely a longer `RESEARCH_USAGE.md`, the benchmark will show no
  additional autonomous trigger behavior.
- If states are ceremonial, responses will name K# but still proceed to MVP;
  rubric credit requires the blocked transition and next operation.
- If subjective triggers constrain nothing, repeated fixtures will not produce
  stable KILL/REDUCE/native-audit decisions; report variance, do not hide it.
- If fixtures overfit satellite terminology, mechanism criteria must still
  apply after every application noun is removed.
- If it duplicates M-* rules, delete duplicated operation instructions and keep
  only state routing and evidence gates.
- If onboarding cost exceeds benefit, keep L1 below 7 KB and load this L2 only
  for new-knowledge tasks.
- If the agent still waits for user wording, fresh-agent treatment fails.
- If it becomes a multi-agent framework, reduce to the sequential tribunal.
- If extraction to a skill appears useful, defer it until repeated
  cross-project evidence and explicit authorization exist.

Apply P7, P11, P18, P22, P28/P29, M-self-application, and
M-add-then-reduce to the final patch. A controller that cannot KILL its own
unnecessary structure has failed its purpose.

Last P20-verified: 2026-08-29
