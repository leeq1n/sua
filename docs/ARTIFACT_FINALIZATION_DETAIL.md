> L0: P30-A4 finalization lifecycle, examples, and evidence limits for artifact promotion.
# Artifact Finalization — Detail

Read [ARTIFACT_FINALIZATION.md](ARTIFACT_FINALIZATION.md) first for the five-step gate.

### P30-A4 post-acceptance liveness

Once the external evaluator has produced the P30-A3 record, the repository's
only post-acceptance entry point is
`finalize_accepted_artifact(external_acceptance_record)` (also exposed as
`--finalize-accepted-artifact`). It consumes the record from outside the
candidate repository, delegates schema/role/decision/identity checks to the
existing verifier, recomputes the clean current identity immediately before
finalization, and rejects any drift or dirty state.

Successful finalization writes one atomic JSON ledger outside the candidate
repository with `ACCEPTED_FROZEN` as its canonical state. The ledger records
the exact accepted commit identity and the reference to the external record;
it does not change the audited tree, create a terminal decision, or claim
`repository_proved_independence = true`. A failed verification or failed
ledger write leaves no new accepted/frozen marker. The old candidate APIs and
automatic loops remain nonterminal and candidate-only.

P30-A3 has two enforcement layers:

- **Machine-enforceable:** computed artifact identity, clean-state requirement,
  drift/staleness, nonterminal local/checker status, external-record schema
  and identity match, and blocked legacy material-finalization paths.
- **Governance/orchestrator-enforced:** fresh evaluator identity, absence of
  hidden authorship, artifact-first ordering, first-pass freezing, and
  independent production of the external report.

The shared `p30_acceptance.py` boundary fails closed when the record is
missing, malformed, stale, dirty, contradictory, or mismatched. It does not
pretend that caller flags prove the governance layer.

Ask: if an informed evaluator encountered only the current artifact, would its
structure and behavior be natural, self-consistent, and appropriate for the
target interface? This is not aesthetic conformity. Preserve every
functionally justified exception and record why it is necessary.

## Mechanism-general examples

- **Software release:** a pinned configuration and several compatibility
  shims pass local tests, but the pin is not externally required. Recover the
  supported-platform objective, remove obsolete shims, regress a previously
  fixed insecure default, and inspect a clean installation before release.
- **Benchmark release:** a fixed row count became a proxy while exclusions and
  metadata changed. Preserve measured records and provenance, challenge the
  presentation count, regress a previously removed leakage class, and audit
  the package without curation history.

## Evidence level

Repository tests validate structure, ordering, scenario coverage, and
discoverability. They do not prove that a live agent will reliably perform a
high-quality blind audit. Until blinded treatment trials are run, report
`STRUCTURALLY_VALIDATED_BEHAVIOR_PENDING`.

## References

- [Acceptance protocol](ACCEPTANCE_PROTOCOL.md)
- [Add then Reduce](ADD_THEN_REDUCE.md)
- [Critical-thinking primitives](M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md)
- [Working principles](PRINCIPLES.md)

Last P20-verified: 2026-09-28
