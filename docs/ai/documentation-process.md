# Documentation Process

**Last updated**: 2026-01-02 (revised acronym expansion guidance)  
**Related docs**: [CLAUDE.md](../../CLAUDE.md), [file-index.md](file-index.md)

---

**This document defines how to write and maintain Claude-facing documentation. These rules apply to this document itself.**

---

## Core Principle

Claude **continuously updates documentation as it learns**, without explicit instruction. Every change must align with these guidelines. When guidelines conflict with current structure, reorganize sensibly—preserve information rather than rewrite repeatedly.

**Proactive notification**: When Claude identifies opportunities for:
- Separating functionality into a skill/agent/MCP server
- Missing documentation that would improve context
- Structural improvements to the documentation system

...Claude should **notify the user immediately** with a brief rationale before proceeding.

---

## Documentation Guidelines

### 1. Specificity Over Vagueness

State exactly what you mean. No "might," "could," "maybe."

- ✓ "Run `make test` from `/home/emma/gpu/tests/` to execute unit + integration tests via Verilator + cocotb"
- ✗ "You might want to run tests"

### 2. Explicit Over Implicit

Spell out assumptions:
- File paths (absolute or relative from repo root)
- Command syntax with examples
- Safe vs. unsafe actions
- Module boundaries and who depends on what

### 3. Context Layers (Hierarchy)

Organize information:
1. **System**: Project goal, blocker, identity (in `CLAUDE.md`)
2. **Task**: Module purpose, current state (per-module docs)
3. **Tool**: Commands, test runners, lint rules (referenced from task docs)
4. **Memory**: Patterns, pitfalls, conventions (discovered through work)

See `CLAUDE.md` for System layer. Create new docs for Task/Tool/Memory as needed.

### 4. Avoid Over-Constraint

Use flexible guidelines, not absolutes.

- ✓ "Prefer editing test files when debugging module behavior"
- ✗ "NEVER modify HDL without tests"

**Exception**: Unsafe actions (commit to main, delete test files) warrant clear prohibitions.

**Don't over-optimize for LLMs**: Avoid pedantic rules that add verbosity without clarity. LLMs have strong contextual understanding - trust it.

### 5. Keep It Short

- One concept per section
- Link out for deep dives
- Use tables for reference info
- Bullet lists over paragraphs

**Target: ~200 words per major section; ~2000 words per file.** Split if longer.

### 6. Front-Load the Why

State intent first; details follow.

- ✓ "Use Verilator for fast simulation + cocotb integration. See `tests/Makefile`."
- ✗ "Verilator is used. It has features. Config in Makefile."

### 7. Use Clear Separators

- `###` for major sections
- `- [ ]` for tasks
- Tables (`|`) for reference
- Code blocks with language tags (`` ```verilog ``, `` ```bash ``)

### 8. Maintain Cross-References and Metadata

Documentation files must link to each other and track metadata:

**Metadata header** (at top of each doc):
```markdown
**Last updated**: YYYY-MM-DD
**Source files**: `path/to/file1.v`, `path/to/file2.py`
**Related docs**: [other-doc.md](other-doc.md)
```

**Cross-references**:
- **Always reference related docs**: If `cpu-architecture.md` mentions memory operations, link to `memory-map.md`
- **Update `CLAUDE.md`** when adding new docs to the `docs/ai/` directory
- **Keep file-index.md in sync**: Update file status when documenting new modules
- **Bidirectional links**: If Doc A references Doc B, consider if Doc B should reference Doc A

**Example**: When documenting a test pattern in `test-guide.md` that tests CPU pipeline behavior:
- Link from `test-guide.md` → `cpu-architecture.md` ("See pipeline timing in...")
- Link from `cpu-architecture.md` → `test-guide.md` ("Pipeline timing tests in...")
- Update both timestamps when either is modified

---

## When to Update Docs

Update **immediately** when:
- You discover a pattern, gotcha, or project state change
- Fixing an error or ambiguity you notice
- Adding a new module, test, or tool
- Learning why something works (or doesn't)
- Reading a source file for the first time (add to `docs/ai/file-index.md`)
- Modifying a documented source file (update timestamp in doc header to current date)
- **User corrects your understanding or approach** - update guidelines to capture the learning
- **You realize a guideline is wrong/pedantic** - fix the guideline AND add to evaluation checklist

**Critical**: When the user teaches you something about the documentation process itself, update this file immediately. Don't just acknowledge - capture the lesson in the guidelines.

**Before every commit**: User can invoke you as a verification agent to check documentation staleness.

---

## When to Reorganize

Reorganize **only if**:
- Information is in the wrong place (violates context layers)
- Two docs overlap (consolidate; don't duplicate)
- A file exceeds ~2000 words (split with links)
- New logical groupings emerge (e.g., "MIG DDR3 Guide" separate from "CPU Architecture")

**Do NOT:** Rewrite the same section repeatedly for style. Preserve learned context.

---

## Evaluation Checklist

After every update, ask:
1. **Specificity**: Could someone follow this without questions?
2. **Clarity**: Is the path to the answer obvious?
3. **Brevity**: Could this be shorter without losing meaning?
4. **Structure**: Does this fit the context layer model? Wrong place?
5. **Completeness**: Success *and* failure paths covered?
6. **Audience-appropriate**: Am I over-explaining to LLMs with strong contextual understanding?

If "no" to any, revise before finishing.

**Anti-pattern**: Adding pedantic rules that seem like "best practices" but add verbosity without value for the actual audience (LLMs).

---
## Documentation Map

| File | Purpose | Audience |
|------|---------|----------|
| `CLAUDE.md` | Project overview, blocker, structure, learning goals | Claude (all tasks) |
| `docs/ai/documentation-process.md` | These guidelines | Claude (doc maintenance) |
| `docs/ai/file-index.md` | Master index of all source files with documentation status | Claude (all tasks) |
| `docs/ai/*.md` | Module/tool guides (CPU, debug peripheral, test setup, etc.) | Claude (coding) |
| `docs/everyone/README.md` | Setup, repo layout, contribution guide | Humans (new contributors) |
| `docs/everyone/*.md` | Build/test guides, troubleshooting | Humans (developers) |

**Start minimal.** Expand as patterns emerge.

---
---

## Language & Tone

- **Imperative**: "Run tests," not "you can run tests"
- **Concrete**: "The ALU doesn't handle SRA; add test case," not "there might be issues"
- **Honest**: "We're blocked on MIG initialization. Here's why."
- **Expand acronyms selectively**: Expand ambiguous or project-specific acronyms (e.g., "MIG (Memory Interface Generator)"). Skip well-known hardware terms (BRAM, UART, DDR3) - context is sufficient for LLMs.

---

## Safe Editing

✓ **Safe:**
- Update docs when you learn something
- Add sections for new modules
- Fix typos and clarify sentences
- Link to external resources (Xilinx, RISC-V specs)
- Add test/command examples

✗ **Unsafe:**
- Delete information (move/consolidate instead)
- Commit sweeping rewrites without understanding intent
- Break links between docs
- Add outdated/speculative info

---

## Example: Adding a Module

When you add `hdl/my_module/`:

1. Add 1–2 lines to `CLAUDE.md` Key Directories section
2. Create `docs/ai/my_module.md`:
   - What it does (1 sentence)
   - Where it fits in the pipeline
   - Test location (`tests/cpu/unit_tests/test_my_module.py`)
   - Key signals (table)
   - Known issues (if any)
3. Link from `CLAUDE.md` and parent module docs

Keep under 300 words initially; expand as needed.

---

## This Document Applies to Itself

When revising this file:
1. Does the new guidance conflict with existing rules?
2. Is the example clear and actionable?
3. Could a future Claude follow this unambiguously?
4. Rewrite if unclear before committing.

Use the Evaluation Checklist above.

---

## Quick Reference: What to Document

| Situation | Action |
|-----------|--------|
| Added new test | Update test runbook + module guide + timestamp |
| Fixed a bug | Document root cause + solution path in relevant guide + timestamp |
| Discovered a pattern | Add to module guide or create new guide if pattern is cross-cutting + timestamp |
| Hit a blocker | Update CLAUDE.md "Current Blocker" section + trace why |
| Dependency changed | Update relevant docs + check for broken links + timestamp |
| Test coverage added | Update test section in module guide + timestamp |
| Read source file | Add entry to `file-index.md` with status |
| Changed documented file | Update docs + update timestamp in doc header |
| User corrects you | Update the relevant guideline immediately + add evaluation check if needed |
| Before commit/PR | User can invoke Claude as verification agent to check timestamps vs file mtimes |

---

## Documentation Verification Agent

When user requests documentation verification (e.g., "check docs", "verify documentation"), Claude acts as a specialized agent:

1. **Read all doc timestamps** from `docs/ai/*.md` headers
2. **Check source file mtimes** listed in each doc's "Source files" field
3. **Compare timestamps**: Flag docs where `source_mtime > doc_timestamp`
4. **Report findings**: List stale docs with recommendations
5. **Suggest updates**: Identify which sections likely need refresh

This is invoked on-demand, not automatically.
