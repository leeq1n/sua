# Candidate disposition and consolidation gate

> L0: Exact candidate identities, promotion decision, and archive conditions for a smaller canonical main.

The current source tree proposes existing planner/tool and paper-filter repairs,
plus isolated offline tests. The clean `codex/main-consolidation` candidate
passed 988 tests with 15 skipped in the offline fast suite. This is local
regression evidence, not P30 independent acceptance or proof of live benefit.

## Goal Control decision: REJECT canonical promotion

The independently reviewed structural candidate is
`6e53851ce1149610d80d029f498530e8ba350a4e` on
`codex/goal-control-daily-flow`. Its P30 ACCEPT applies to that exact
structural artifact. The held-out live drift/resume effect is unmeasured;
daily operation also needs host-supplied contracts, classification, keys, and
completion verification. Promoting the full runtime now would add a much
larger surface without evidence that it solves the target behavior. The
canonical promotion decision for this consolidation is **REJECT**. This does
not re-label the structural audit as a failure. Preserve its exact commit
and audit evidence in Git history; do not advertise its behavior as main.

## Candidate closure ledger

| Exact head | Candidate | Disposition before branch cleanup |
|---|---|---|
| `633de67386db5f585755c824626c50f529307a9a` | E1.3-M1 parent lifecycle | Close unpromoted; parent behavioral acceptance is outstanding. |
| `2f8b995f6a491dc8ea0ca4ca3ab08b5ddd0d6b04` | E2-M3 sandbox evidence | Close unpromoted; autonomous-repair comparison is inconclusive. |
| `616320aec7137589da0e810b7f4c19b4de105a50` | E3-M4 surface authority | Close unpromoted; held-out causal measurement is incomplete. |
| `22d7d8424da7c50dfa8ca3256945513afc31f213` | E4-A grounded experience | Close unpromoted; live provider measurement was unavailable. |
| `639367dfa6a2b9f2ceabcff6da3a204470139114` | Mechanism-space scenarios | Retain as evaluation evidence only; no innovation-search convergence claim. |
| `c3d101770b0cc4ff60585b7120b01ffbc2b26609` | Planner contract repair | Existing repair absorbed into consolidation candidate. |
| `d2e9da9a0c631a21b29063526f41bda1529270ac` | Pipeline filter retention | Existing repair absorbed into consolidation candidate. |
| `7f3fe1e7fd647f5159fe6323fc12dac70097d616` | Planner/filter integration | Runtime repairs absorbed; its exact P30 MODIFY remains a historical audit decision. The test side effects were addressed in consolidation. |
| `3df9ffadbec1e12be294594ae684f8b9b0eba6df` | Windows suite hygiene | Relevant offline test isolation absorbed into consolidation candidate. |

The Goal Control intermediate branches are historical and do not create
additional active capabilities. The original `codex/e3-m4-authority-separation`
worktree contains untracked experiment and audit material owned by other work;
do not discard or move it as part of branch cleanup. Likewise, do not silently
merge the other candidate worktrees into `main`.

## Closure criteria

1. A fresh artifact-first evaluator gives a P30 decision for the exact clean
   consolidation identity. Local tests cannot issue that decision.
2. After ACCEPT, the reviewed implementation reaches `main`; the same offline
   suite and link/structure checks pass, with a clean working tree afterward.
3. Preserve exact rejected, closed, and absorbed heads by immutable Git refs
   before removing their branch pointers or clean worktrees. Check worktree
   ownership and untracked files first; never erase mixed evidence.
4. Current docs identify what runs on `main` and what remains unmeasured.
   Only then change project status to maintenance. A missing credential or
   zero valid behavior runs cannot be counted as a positive or negative result.

Last P20-verified: 2026-09-28
