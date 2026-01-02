# Claude Documentation

**Last updated**: 2026-01-02

This project includes structured documentation for Claude (AI) and for humans.

## Documentation Map

**For all tasks**: Start with [documentation-process.md](docs/ai/documentation-process.md) for maintenance rules.

**By topic**:
- **Architecture**: [cpu-architecture.md](docs/ai/cpu-architecture.md), [memory-map.md](docs/ai/memory-map.md), [axi-interface.md](docs/ai/axi-interface.md)
- **Testing**: [test-guide.md](docs/ai/test-guide.md), [coverage.md](docs/ai/coverage.md)
- **Debug**: [debug-protocol.md](docs/ai/debug-protocol.md)
- **File tracking**: [file-index.md](docs/ai/file-index.md)

**For humans**: [docs/everyone/](docs/everyone/) (setup guides, troubleshooting)

---

## Project Overview

**Goal**: Build a minimal computer on an Arty S7-50 FPGA with a soft-core RISC-V CPU, VGA video output, and debug capabilities via UART.

### Current State

- **CPU**: RV32I (no M/F/D extensions, no multiplication) – **not yet booting**
- **Tests**: Unit tests written and passing; integration tests in progress
- **Memory**: Working on DDR3 (MIG) initialization; currently **blocked here**
- **Video**: VGA output module exists; framebuffer designed but not yet DDR3-backed
- **Debug**: UART-based debug peripheral under development (`tools/debugger`) for halt/reset/register inspection
- **Peripherals**: Planned for post-DDR3 (game/networking TBD)

### Current Blocker

**MIG (Memory Interface Generator) DDR3 initialization** – need to get the soft core reading/writing DRAM before framebuffer can be useful.

### Repository Structure

```
hdl/                    # Verilog HDL sources
├── cpu/                # RISC-V RV32I soft core (see cpu-architecture.md)
├── debug_peripheral/   # UART debug interface (see debug-protocol.md)
├── framebuffer.v       # Dual framebuffer for VGA
├── vga_out.v          # VGA signal generation
└── gpu.v              # Top-level module

tests/                  # Verilator + cocotb tests (see test-guide.md)
├── cpu/unit_tests/     # ~14 module-level tests
├── cpu/integration_tests/  # ~40+ instruction tests
└── Makefile           # Run: cd tests && make

tools/
├── debugger/          # Go CLI for UART debug (see debug-protocol.md)
└── compiler/          # Placeholder for RISC-V toolchain

docs/
├── ai/                # Claude-facing documentation
└── everyone/          # Human-facing guides

config/
└── arty-s7-50.xdc    # FPGA constraints (pins, clocks, ILA debug cores)
```

**For detailed file listings**: See [file-index.md](docs/ai/file-index.md)

### Documentation Workflow

**Critical**: Update docs continuously as you learn. Before finalizing any work:

1. Check [documentation-process.md](docs/ai/documentation-process.md) for guidelines
2. Update affected docs to reflect new learning
3. Update timestamps in doc headers (`YYYY-MM-DD`)
4. Update [file-index.md](docs/ai/file-index.md) if documenting new files

**Common task patterns**:
- **MIG/DDR3 issues**: Add findings to "Current Blocker" section above or create `docs/ai/mig-ddr3.md`
- **CPU logic**: Document patterns in module-specific `docs/ai/*.md`
- **Debug protocol**: Update [debug-protocol.md](docs/ai/debug-protocol.md) when protocol changes
- **Constraints/timing**: Document in `docs/ai/fpga-constraints.md`

**Verification**: Use "check docs" to verify staleness before commits (compare timestamps vs file mtimes)
