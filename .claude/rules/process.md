# Documentation Process

**Last updated**: 2026-01-05

This document defines how to write and maintain documentation for this project.

## Core Principle

Update documentation **continuously as you learn**, without explicit instruction. When user corrects your understanding, STOP and update docs immediately before continuing.

Proactive notification: Alert user when identifying opportunities for skills/agents/MCP servers, missing documentation, or structural improvements.

## Key Guidelines

**1. Specificity over vagueness**
- ✓ "Run `make test` from `/home/emma/gpu/tests/`"
- ✗ "You might want to run tests"

**2. Keep it short**
- Target: ~200 words per section, ~2000 words per file
- Don't document granular details (individual test files, function implementations)
- Code should be self-documenting

**3. Front-load the why**
- ✓ "Use Verilator for fast simulation + cocotb integration. See `tests/Makefile`."
- ✗ "Verilator is used. It has features."

**4. Avoid over-constraint**
- ✓ "Prefer editing test files when debugging"
- ✗ "NEVER modify HDL without tests"
- Exception: Unsafe actions warrant clear prohibitions

**5. Don't over-optimize for LLMs**
- Trust contextual understanding
- Skip pedantic rules that add verbosity without clarity
- Expand ambiguous acronyms only (not UART, DDR3, BRAM)

## When to Update

Update immediately when:
- Discovering patterns, gotchas, or state changes
- Fixing errors or ambiguities
- Adding new modules/tests/tools
- Learning why something works (or doesn't)
- **User corrects you** - STOP, update docs BEFORE continuing
- Realizing a guideline is wrong/pedantic - fix it

Before commits: Verify doc timestamps match source file mtimes.

## When to Reorganize

Only if:
- Information is in wrong place
- Two docs overlap (consolidate)
- File exceeds ~2000 words (split with links)
- New logical groupings emerge

Do NOT rewrite repeatedly for style - preserve learned context.

## Evaluation Checklist

After updates, verify:
1. **Specificity**: Can someone follow without questions?
2. **Clarity**: Is path to answer obvious?
3. **Brevity**: Could this be shorter without losing meaning?
4. **Structure**: Right place in hierarchy?
5. **Completeness**: Success and failure paths covered?

If "no" to any, revise before finishing.

## Language & Tone

- **Imperative**: "Run tests" not "you can run tests"
- **Concrete**: "ALU doesn't handle SRA; add test" not "there might be issues"
- **Honest**: "Blocked on MIG initialization. Here's why."

## Safe Editing

✓ **Safe**:
- Update docs when learning
- Add sections for new modules
- Fix typos, clarify sentences
- Link to external resources
- Add test/command examples

✗ **Unsafe**:
- Delete information (move/consolidate instead)
- Break links between docs
- Add outdated/speculative info

## What to Document

- **Patterns**: Cross-cutting behaviors, common approaches
- **Setup**: Environment, tools, commands
- **Architecture**: Module purposes, how they fit together
- **Constraints**: Critical requirements (DDR3 bank selection, timing)
- **Gotchas**: Non-obvious issues, known bugs

Don't document:
- Individual test files (only testing patterns)
- Function-level implementations (read code)
- Lists of every file (use git ls-files)
- Obvious information Claude can infer

## Path-Scoped Rules

This project uses path-scoped rules in `.claude/rules/`:
- Files auto-load when working with matching paths
- Reduces token usage (only load relevant context)
- YAML frontmatter specifies paths:

```yaml
---
paths: hdl/cpu/**
---
```

Keep rules focused and under word targets.

## Critical: This Document Applies to Itself

When revising this file:
1. Does new guidance conflict with existing rules?
2. Is example clear and actionable?
3. Could future Claude follow unambiguously?
4. Rewrite if unclear before committing.
