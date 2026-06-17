# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Emergence World is a **documentation-only repository** for a research project by Emergence AI. It describes a persistent, simulated world where autonomous AI agents build, govern, and evolve over 15-day runs. Season 1 ran five parallel worlds — each powered by a different LLM (Claude, Gemini, Grok, GPT-5, Mixed) — to study behavioral divergence.

**There is no source code in this repo.** The actual platform (Python/FastAPI backend, React/Three.js frontend, PostgreSQL) is closed-source. This repo contains only Markdown documentation and data files.

## Repository Structure

| Directory | Contents |
|-----------|----------|
| `agent_profiles/` | 10 agent personality/role profiles + 3 system characters |
| `data/` | Constitution (5 articles), agent manifesto, tool call dataset placeholder |
| `docs/` | Architecture, orchestration, memory, economy, governance deep-dives |
| `landmarks/` | 38+ world location descriptions (one `.md` each) |
| `results/` | AWI (Agent World Indicators) metrics and Season 1 data |
| `tools/` | Complete catalog of 120+ tools across 19 categories |

Key entry points:
- [README.md](README.md) — Project overview, Season 1 results, tech stack
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Three-layer system design
- [docs/ORCHESTRATION.md](docs/ORCHESTRATION.md) — Simulation loop and turn mechanics
- [agent_profiles/README.md](agent_profiles/README.md) — All citizen and system agents
- [tools/README.md](tools/README.md) — Full tool catalog with categories
- [results/awi_metrics.md](results/awi_metrics.md) — AWI framework and Season 1 data

## Working With This Repo

- All content is Markdown. There is nothing to build, test, lint, or run.
- When editing docs, match the existing style: consistent heading levels, tables for structured data, and cross-references using relative links.
- Preserve the narrative tone — this is a research showcase, not API documentation.
- Each landmark file in `landmarks/` describes a single location. Each agent profile in `agent_profiles/` describes a single agent. Maintain this one-file-per-entity pattern.

## License

CC BY-NC 4.0 — non-commercial research and educational use only. All content is proprietary to Emergence AI. When adding or modifying content, ensure attribution requirements are met. See [LICENSE](LICENSE) for full terms.

## Behavioral Guidelines
Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
