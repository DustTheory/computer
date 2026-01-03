# File Index

**Last updated**: 2026-01-02  
**Purpose**: Master index of all source files with documentation status and last modified timestamps.

---

This file tracks which source files have been read/documented. Each documentation file contains a "Last updated" timestamp that Claude compares against file modification times to detect staleness.

## Status Legend

- ✅ **Documented** - File read, documented in AI docs
- 📖 **Partially documented** - Some aspects covered, but incomplete
- ⏳ **Planned** - Identified for documentation, not yet written
- ❌ **Not covered** - File exists but not yet examined

## HDL Files

### CPU Core (`hdl/cpu/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `cpu.v` | ✅ | cpu-architecture.md | HEAD | 3-stage pipeline, stall logic |
| `cpu_core_params.vh` | 📖 | cpu-architecture.md | HEAD | Referenced but not fully documented |
| `arithmetic_logic_unit/arithmetic_logic_unit.v` | ⏳ | - | Never | Mentioned in cpu-architecture.md |
| `arithmetic_logic_unit/arithmetic_logic_unit.vh` | ❌ | - | Never | - |
| `comparator_unit/comparator_unit.v` | ⏳ | - | Never | Mentioned in cpu-architecture.md |
| `comparator_unit/comparator_unit.vh` | ❌ | - | Never | - |
| `control_unit/control_unit.v` | ⏳ | - | Never | Decoding logic not documented |
| `control_unit/control_unit.vh` | ❌ | - | Never | - |
| `immediate_unit/immediate_unit.v` | ⏳ | - | Never | - |
| `immediate_unit/immediate_unit.vh` | ❌ | - | Never | - |
| `instruction_memory/instruction_memory_axi.v` | 📖 | cpu-architecture.md | Never | Mentioned but not detailed |
| `memory/memory_axi.v` | ✅ | axi-interface.md, memory-map.md | HEAD | Full AXI state machine documented |
| `memory/memory.vh` | ✅ | axi-interface.md, memory-map.md | HEAD | Load/store types documented |
| `register_file/register_file.v` | 📖 | cpu-architecture.md | Never | Mentioned but not detailed |

### Debug Peripheral (`hdl/debug_peripheral/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `debug_peripheral.v` | ✅ | debug-protocol.md | HEAD | UART command state machine |
| `debug_peripheral.vh` | ✅ | debug-protocol.md | HEAD | Opcodes documented |
| `uart_receiver.v` | 📖 | debug-protocol.md | Never | Mentioned, not detailed |
| `uart_transmitter.v` | 📖 | debug-protocol.md | Never | Mentioned, not detailed |
| `spec.txt` | ❌ | - | Never | Noted as outdated in docs |

### Top Level (`hdl/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `gpu.v` | ❌ | - | Never | Top-level module |
| `framebuffer.v` | ❌ | - | Never | VGA framebuffer |
| `vga_out.v` | ❌ | - | Never | VGA signal generation |
| `instruction_engine/instruction_engine.v` | ❌ | - | Never | Legacy? Status unclear |

### Support Files (`hdl_inc/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `axil_ram.v` | 📖 | test-guide.md | Never | Test fixture mentioned |

## Test Files

### Unit Tests (`tests/cpu/unit_tests/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `cpu_unit_tests_harness.v` | 📖 | test-guide.md | Never | Harness mentioned |
| `test_arithmetic_logic_unit.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_comparator_unit.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_immediate_unit.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_register_file.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_control_unit.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_instruction_memory_axi.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_memory_axi.py` | ✅ | test-guide.md, axi-interface.md | HEAD | Example pattern documented |
| `test_uart_receiver.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_uart_transmitter.py` | 📖 | test-guide.md | Never | Listed, not detailed |
| `test_debug_peripheral.py` | ✅ | test-guide.md, debug-protocol.md | HEAD | Example documented |

### Integration Tests (`tests/cpu/integration_tests/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `cpu_integration_tests_harness.v` | 📖 | test-guide.md | Never | Harness mentioned |
| `test_add_instruction.py` | ✅ | test-guide.md | HEAD | Example pattern documented |
| All other `test_*_instruction.py` | 📖 | test-guide.md | Never | Listed but not detailed |

### Test Support (`tests/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `Makefile` | ✅ | test-guide.md | HEAD | Targets documented |
| `rom.mem` | 📖 | test-guide.md, memory-map.md | Never | Mentioned |
| `cpu/constants.py` | ✅ | test-guide.md, cpu-architecture.md, memory-map.md | 56d2744 | Constants documented |
| `cpu/utils.py` | ✅ | test-guide.md | HEAD | Functions documented |

## Tools

### Debugger (`tools/debugger/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `main.go` | 📖 | debug-protocol.md | Never | Mentioned |
| `commands.go` | ✅ | debug-protocol.md | HEAD | Commands documented |
| `serial.go` | ✅ | debug-protocol.md | HEAD | Serial interface documented |
| `opcodes.go` | ✅ | debug-protocol.md | HEAD | Opcodes documented |
| `ui.go` | 📖 | debug-protocol.md | Never | Mentioned |
| `logger.go` | 📖 | debug-protocol.md | Never | Mentioned |

### Compiler (`tools/compiler/`)

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| All files | ❌ | - | Never | Empty/placeholder directory |

## Configuration Files

| File | Status | Docs Reference | Last Read Commit | Notes |
|------|--------|----------------|------------------|-------|
| `config/arty-s7-50.xdc` | ❌ | CLAUDE.md | Never | Mentioned only |
| `verilator.vlt` | ❌ | CLAUDE.md | Never | Mentioned only |
| `.coding-style.f` | ❌ | CLAUDE.md | Never | Mentioned only |

## Coverage Summary

**HDL Files**:
- Total: 18 .v files
- ✅ Documented: 4 (22%)
- 📖 Partially: 8 (44%)
- ⏳ Planned: 3 (17%)
- ❌ Not covered: 3 (17%)

**Test Files**:
- Total: ~50 test files + 2 harnesses
- ✅ Documented: 5 (10%)
- 📖 Partially: ~45 (90%)

**Tools**:
- ✅ Debugger: 60% coverage
- ❌ Compiler: 0% coverage

## Update Workflow

**Before every commit/PR**:
1. Run: `git diff --name-only HEAD` to see changed files
2. For each changed file in this tracker, mark as 🔄 **Needs update**
3. Review affected documentation sections
4. Update docs to reflect changes
5. Update "Last Read Commit" column to HEAD
6. Change status back from 🔄 to ✅

**When documenting a new file**:
1. Read the file completely
2. Add/update relevant AI documentation
3. Update this tracker with ✅ status
4. Record current commit hash in "Last Read Commit"

**When a gap is identified**:
1. Mark file as ⏳ **Planned** with notes about what needs documenting
2. Prioritize based on importance to current work
