# INDEX — full navigation map

> L0: Navigation index for the docs in `/docs/`.  Each entry:
> doc (summary) + companion (DETAIL) + TL;DR.  Read summary
> first; click through to detail only as needed.
> When any file in /docs/ is added/removed/renamed, update this
> index (per P14 docs stay current).

## Reading order for a fresh agent

1. **core-layer/AGENTS_CORE.md** — always-loaded contract and authoritative
   "Read first" sequence.
2. **AGENTS.md** (root) — project-specific operating-rule index.
3. Follow the "Read first" sequence in `core-layer/AGENTS_CORE.md`; use the
   map below to locate each document when needed.

## L0: Entry / orientation

| Doc | Companion | TL;DR |
|---|---|---|
| [../AGENTS.md](../AGENTS.md) | [../AGENTS_DETAIL.md](../AGENTS_DETAIL.md) | Operating rules for AI agents in this repo |
| [INDEX.md](INDEX.md) | [INDEX_DETAIL.md](INDEX_DETAIL.md) | Full navigation map |
| [PROJECT_STATE.md](PROJECT_STATE.md) | [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md) | Goal + current state + next step |
| [CANDIDATE_STATUS.md](CANDIDATE_STATUS.md) | (self-contained) | Canonical baseline and isolated candidate boundaries |
| [CONSTRAINTS.md](CONSTRAINTS.md) | [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Invariants the system must preserve |
| [USER_INSIGHTS.md](USER_INSIGHTS.md) | [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md) | Paraphrased user rules + verbatim quotes |
| [HOW_TO_READ_GRAPH.md](HOW_TO_READ_GRAPH.md) | [HOW_TO_READ_GRAPH_DETAIL.md](HOW_TO_READ_GRAPH_DETAIL.md) | Read pattern for new agents (L0 → L1 → L2) |
| [SWITCH_SIGNALS.md](SWITCH_SIGNALS.md) | (within file) | Switch signals + action protocol |

## L1: Principles / rules

| Doc | Companion | TL;DR |
|---|---|---|
| [PRINCIPLES.md](PRINCIPLES.md) | [PRINCIPLES_FULL.md](PRINCIPLES_FULL.md) | Working principles (L0/L1) + per-P-n 实操 (L2) |
| [PRINCIPLES_DETAIL.md](PRINCIPLES_DETAIL.md) | [PRINCIPLES_FULL.md](PRINCIPLES_FULL.md) | L2 routing index; P30 routes to its canonical full section |
| [OPERATING_RULES.md](OPERATING_RULES.md) | [OPERATING_RULES_DETAIL.md](OPERATING_RULES_DETAIL.md) | M-n operating rules (workflow discipline) |
| [EXTENSIONS.md](EXTENSIONS.md) | [EXTENSIONS_DETAIL.md](EXTENSIONS_DETAIL.md) | Extension rules (L0/L1/L2 + extensions) |
| [RECURSIVE_DECOMPOSITION.md](RECURSIVE_DECOMPOSITION.md) | (within file) | Top-down decomposition rules |
| [RECURSIVE_QUALITY.md](RECURSIVE_QUALITY.md) | (within file) | Recursive quality loop (拆解+类比+自指) |
| [ADD_THEN_REDUCE.md](ADD_THEN_REDUCE.md) | (within file) | Add-then-reduce operational pattern |
| [SUMMARY_LIFECYCLE.md](SUMMARY_LIFECYCLE.md) | (within file) | Summary lifecycle (destroy contract) |
| [PRINCIPLE_COLLAPSE_PREVENTION.md](PRINCIPLE_COLLAPSE_PREVENTION.md) | (within file) | 原则防崩塌 guardrails |
| [SELF_ORG.md](SELF_ORG.md) | (within file) | Self-organization patterns (P27) |
| [COMMON_PITFALLS.md](COMMON_PITFALLS.md) | (within file) | Common pitfalls observed in project history |

## L2: M-n detail files

The complete M-n detail-file map is in [INDEX_DETAIL.md](INDEX_DETAIL.md).
Load it only when an M-n rule needs its L2 companion.

## L1: Operational patterns / knowledge

| Doc | Companion | TL;DR |
|---|---|---|
| [KNOWLEDGE_ORG.md](KNOWLEDGE_ORG.md) | [KNOWLEDGE_ORG_DETAIL.md](KNOWLEDGE_ORG_DETAIL.md) | Knowledge organization (taxonomy) |
| [MODEL_STRATEGY.md](MODEL_STRATEGY.md) | [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md) | Which LLM, why, deployment notes |
| [LITERATURE.md](LITERATURE.md) | [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Papers read + how they constrain design |
| [MCP_TOOLS.md](MCP_TOOLS.md) | (within file) | MCP tool ecosystem + which tools to use when |
| [MEMORY_TOOLS.md](MEMORY_TOOLS.md) | (within file) | Memory system usage patterns |
| [SKILLS.md](SKILLS.md) | (within file) | Skill lifecycle / SkillOpt paper mapping |
| [SKILL_DESIGN.md](SKILL_DESIGN.md) | [SKILL_DESIGN_DETAIL.md](SKILL_DESIGN_DETAIL.md) | Skill design + incubation framework |
| [CROSS_RUNTIME_SKILL_BRIDGE.md](CROSS_RUNTIME_SKILL_BRIDGE.md) | (within file) | Agent Skills SKILL.md bridge for non-canonical runtimes |
| [RESEARCH_USAGE.md](RESEARCH_USAGE.md) | (within file) | 科研项目适配器模式 + 工作流 |
| [AI4S_RESEARCH_MODE.md](AI4S_RESEARCH_MODE.md) | [AI4S_RESEARCH_MODE_DETAIL.md](AI4S_RESEARCH_MODE_DETAIL.md) | Scientific-state controller for new-knowledge tasks |
| [AI4S_PHASE_A_VALIDATION.md](AI4S_PHASE_A_VALIDATION.md) | (within file) | Phase A evidence, limitations, and layer decision |
| [DOMAIN_SPECIALIZATION_BOOTSTRAP.md](DOMAIN_SPECIALIZATION_BOOTSTRAP.md) | [DOMAIN_SPECIALIZATION_BOOTSTRAP_DETAIL.md](DOMAIN_SPECIALIZATION_BOOTSTRAP_DETAIL.md) | Detect recurring domain-methodology gaps before adapter incubation |
| [HANDOFF.md](HANDOFF.md) | [HANDOFF_DETAIL.md](HANDOFF_DETAIL.md) | Project handoff template |
| [ACCEPTANCE_PROTOCOL.md](ACCEPTANCE_PROTOCOL.md) | [ACCEPTANCE_PROTOCOL_DETAIL.md](ACCEPTANCE_PROTOCOL_DETAIL.md) | Acceptance protocol |
| [ARTIFACT_FINALIZATION.md](ARTIFACT_FINALIZATION.md) | (within file) | Bounded final-promotion gate for evidence-bearing artifacts |
| [ARTIFACT_GOVERNANCE_VALIDATION.md](ARTIFACT_GOVERNANCE_VALIDATION.md) | (within file) | Tribunal evidence, reduction decision, and validation limits |
| [ANALYSIS_PARENT_VERIFY.md](ANALYSIS_PARENT_VERIFY.md) | [ANALYSIS_PARENT_VERIFY_DETAIL.md](ANALYSIS_PARENT_VERIFY_DETAIL.md) | Parent verification analysis |
| [TODO_SESSION_PERSISTENCE.md](TODO_SESSION_PERSISTENCE.md) | [TODO_SESSION_PERSISTENCE_DETAIL.md](TODO_SESSION_PERSISTENCE_DETAIL.md) | Session persistence proposal (M-context-snapshot design) |

## Domain-specific / utility

| Doc | TL;DR |
|---|---|
| [PRINCIPLES_DETAIL_DETAIL.md](PRINCIPLES_DETAIL_DETAIL.md) | Per-P-n detail (L2 deep) |
| [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Constraints (L2 deep) |
| [EXTENSIONS_DETAIL.md](EXTENSIONS_DETAIL.md) | Extensions (L2 deep) |
| [HANDOFF_DETAIL.md](HANDOFF_DETAIL.md) | Handoff (L2 deep) |
| [KNOWLEDGE_ORG_DETAIL.md](KNOWLEDGE_ORG_DETAIL.md) | Knowledge org (L2 deep) |
| [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Literature (L2 deep) |
| [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md) | Model strategy (L2 deep) |
| [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md) | User insights (L2 deep) |
| [SKILL_DESIGN_DETAIL.md](SKILL_DESIGN_DETAIL.md) | Skill design (L2 deep) |
| [M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md](M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md) | Sub-project experiment (L2 deep) |
| [M_TERMINOLOGY_CLARITY_DETAIL.md](M_TERMINOLOGY_CLARITY_DETAIL.md) | Terminology clarity (L2 deep) |

## Plans

| Doc | TL;DR |
|---|---|
| [PLANS/PLAN_2026-07-30.md](PLANS/PLAN_2026-07-30.md) | Historical ATDD plan from 2026-07-30 |

## See also

- **AGENTS.md** (root L0 entry doc)
- **core-layer/README.md** — 3-layer governance (核心/用户/项目)
- **core-layer/AGENTS_CORE.md** — always-loaded contract

Last P20-verified: 2026-09-28
