# Self-Upgrade Agent (SUA)

> **Canonical repository:** [`leeq1n/sua`](https://github.com/leeq1n/sua) is the active source of truth for SUA. [`leeq1n/self-upgrade-agent`](https://github.com/leeq1n/self-upgrade-agent) is the legacy predecessor and is no longer an active development source.



[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](CONTRIBUTING.md)
[![AAIF Compatible](https://img.shields.io/badge/AAIF-AGENTS.md%20compatible-blueviolet)](AGENTS.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard%202025--12--18-success)](docs/CROSS_RUNTIME_SKILL_BRIDGE.md)
[![Latest Release](https://img.shields.io/github/v/release/leeq1n/sua?label=latest&color=green)](https://github.com/leeq1n/sua/releases/latest)


> L0: SUA project README — orientation, current state.

> SUA aims to be a **cross-runtime, long-term Agent Control Plane**. Its current
> canonical delivery is an agent discipline knowledge library — agent
> behavior rules, reasoning primitives, and operating principles
> that you can carry into any agent runtime.

The control-plane work is being developed in isolated candidates. See
[`docs/CANDIDATE_STATUS.md`](docs/CANDIDATE_STATUS.md) for the current `main`
boundary and what remains unverified.



## What is SUA?



SUA packages three categories of agent knowledge:



1. **Agent behavior rules** — working principles and operational

   rules that any agent on this contract should follow.

2. **Reasoning primitives** — critical/constructive thinking

   primitives used to evaluate and build.

3. **Operating conventions** — how a new agent onboards, how

   commits are structured, how rules evolve.



The agent reads these on session start and uses them to constrain

its behavior.



## Quick start (new agent)



1. Read `core-layer/AGENTS_CORE.md`, then `AGENTS.md` (operating rules)

2. Read `docs/HOW_TO_READ_GRAPH.md` (3-step read pattern)

3. Read `docs/HANDOFF.md` (project-specific onboarding)

4. Read `docs/PROJECT_STATE.md` Goal section (current state)

5. Read `docs/PRINCIPLES.md` (L0 + L1 layer only)

6. Optional: `docs/SKILL_DESIGN.md` (if designing or

   incubating a new skill)



Total: ~30 min onboarding.



**For non-canonical runtimes** (Cursor / Codex / Antigravity

that prefer the Agent Skills `SKILL.md` format, or stateless

sessions that need a one-line entry point), see

[`docs/CROSS_RUNTIME_SKILL_BRIDGE.md`](docs/CROSS_RUNTIME_SKILL_BRIDGE.md).

The bridge is a convenience layer; the 6-step workflow above is

the canonical SUA onboarding.



### What the agent gets



- `core-layer/AGENTS_CORE.md` — cache-stable, always-loaded rules

- `AGENTS.md` — per-task operating-rule index

- `agent-tools/scripts/` — self-audit + verification tooling

  (self_health_check, validate_links, validate_structure,

  token_budget, cross_repo_audit, run_acceptance)



The agent loads the core and relevant project rules at session start;
scripts are used when verification is needed.



## Working principles (P-n) + workflow (M-n)



See `docs/PRINCIPLES.md` (P1-P30 working principles, with

P1-P30 referenced across docs). The commit-message hook

enforces P-n cite in commit messages.



See `docs/OPERATING_RULES.md` (M-* operating workflow rules:

M-task-summary, M-must-read, M-context-snapshot,

M-subtask-summary, M-intent-parsing, M-learn,

M-add-then-reduce, M-self-audit, M-self-application).



## Contributing



Contributions should follow the operating rules in `AGENTS.md`.

The commit-message hook enforces that every commit message

follows the contract.



See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution

workflow and acceptance protocol.



## Detailed content (L2)



For full project history, CLI documentation, code architecture,

version history, and other L2 detail, see

[`README_DETAIL.md`](README_DETAIL.md). Per the R6 split rule,

this companion is required when the README exceeds 7 KB.



## Code legacy



This project was originally a self-improving agent that modifies

`core/planner.py`. The code still exists and is functional, but

is no longer the project's focus. For code documentation and CLI

usage, see `README_DETAIL.md` § Code legacy.



## Changelog



For the full history of SUA development, see

[`CHANGELOG.md`](CHANGELOG.md).



## Code of conduct



Participation in this project is governed by the

[Contributor Covenant](CODE_OF_CONDUCT.md), version 2.1.



## License



This project is licensed under the [MIT License](LICENSE)

(c) 2026 LiQin.



## Status



This repo is the default direct-use path: clone it into your
project, point your agent at `core-layer/AGENTS_CORE.md`, and load
`AGENTS.md` for the task-specific contract.



## Install



**Clone 用法（推荐，任何 agent 通用）**: SUA 不需要"安装"，

直接放进项目目录即可：



```bash

# 在你的项目里 (如科研项目 satellite-security/)

git clone https://github.com/leeq1n/sua.git .sua/



# 对 agent 说：用 .sua/ 约束你的行为

# 先读 .sua/core-layer/AGENTS_CORE.md，再按任务读 .sua/AGENTS.md

```



### Existing projects migrating from the legacy repository

If an existing project’s `.sua/` checkout still points to the legacy
repository, inspect its state first, then update the remote safely:

```bash
cd .sua
git remote -v
git remote set-url origin https://github.com/leeq1n/sua.git
git fetch origin
```

Review `git status` and `git log` before choosing any rebase or reset; this
migration does not require destructive replacement of local history.

**跨 agent 使用教程**：



| Agent | 用法 |

|---|---|

| **Hermes / Cursor** | 项目内 clone `.sua/`，按本 README Quick start 读取 core 与项目规则 |

| **Codex / Claude Code / Antigravity** | 见 [`docs/CROSS_RUNTIME_SKILL_BRIDGE.md`](docs/CROSS_RUNTIME_SKILL_BRIDGE.md)（Agent Skills `SKILL.md` 格式桥接） |

| **任意 stateless 会话** | 用 bridge 的 system-prompt 注入方式 |

| **科研项目** | 通用接入见 [`docs/RESEARCH_USAGE.md`](docs/RESEARCH_USAGE.md)；发现、证伪或声称新知识时先加载 [`docs/AI4S_RESEARCH_MODE.md`](docs/AI4S_RESEARCH_MODE.md) |



**Hook 安装（可选）**: 想让 SUA 的 commit-msg / pre-commit

等 hooks 在你的项目生效。**一条命令**（hooks + 依赖自动

处理，目标项目零污染 — 不会出现 `agent-tools/` 目录）：



```bash

# macOS / Linux / Git Bash:

bash .sua/install-hooks.sh



# Windows (cmd / PowerShell，无需 bash):

.sua\install-hooks.bat

# 或双击 install-hooks.bat

```



覆盖已存在的 hooks 加 `--force`；预览加 `--dry-run`。



> 注：install-hooks.sh / .bat 会把 hook 内的脚本路径重写

> 到 SUA clone 内部（`.sua/agent-tools/scripts/`），你的项目只

> 增加 `.git/hooks/` 条目，不产生任何 `agent-tools/` 目录（对

> codex / claude 等 agent 友好）。Windows 下 .bat

> 自动定位 git 自带的 bash 并处理路径转换（cygpath）。



## Uninstall



**Clone 用法（推荐）**: SUA 通过 `git clone` 放进项目目录，

移除 = 删除 `.sua/` 目录即可（无残留，因为 clone 不改动

项目自身的 git hooks）。



**Hook 安装用法**: 仅当你用 install-hooks.sh 安装过 hooks，

才需要清理：



```bash

# 移除 hooks（目标项目没有 agent-tools/，无需清理其他）

rm .git/hooks/commit-msg .git/hooks/pre-commit .git/hooks/prepare-commit-msg .git/hooks/pre-push

```
