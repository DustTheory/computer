# GPU FPGA Project

**Last updated**: 2026-05-23

Minimal computer on Arty S7-50 FPGA: RISC-V RV32I soft core + VGA video + UART debug.

## Current Status

- **CPU**: RV32I (no M/F/D extensions), unit + integration tests passing
- **Memory**: DDR3 operational @ 81.25 MHz (MIG initialized 2026-01-04)
- **Video**: VGA working — DDR3-backed framebuffer via VDMA
- **Debug**: UART debug peripheral working (`tools/debugger`, `tools/probe.py`)
- **Blocker**: None

## Quick Start

```bash
# Run tests
cd tests && source test_env/bin/activate && make

# Debug via UART
go run tools/debugger/main.go

# Build (future - not yet set up)
# cd tools/compiler && make
```

## Key Directories

- `hdl/` - Verilog sources (cpu/, debug_peripheral/, vga_out/)
- `tests/` - Verilator + cocotb tests (unit_tests/, integration_tests/)
- `tools/` - debugger/ (Go UART CLI), probe.py (Python monitor)
- `config/` - arty-s7-50.xdc (pin constraints), mig_b.prj (MIG config)
- `ip_repo/` - Packaged CPU IP for Vivado block design
- `docs/` - Architecture and getting started guides

## Documentation System

This project uses **path-scoped rules** in `.claude/rules/` that auto-load when you work with matching files:

- **Always loaded**: `.claude/rules/process.md` (documentation workflow)
- **When editing CPU**: `.claude/rules/architecture/cpu.md`
- **When editing memory**: `.claude/rules/architecture/memory.md`
- **When editing tests**: `.claude/rules/testing/tests.md`
- **When editing debug**: `.claude/rules/debug/debug.md`
- **When editing constraints**: `.claude/rules/architecture/mig-vivado.md`

You don't need to manually read docs - the relevant rules load automatically based on which files you're working with.

## Critical Constraints

- **DDR3**: Requires 200 MHz ref_clk, Bank 34 only (voltage isolation)
- **UART**: 115200 baud @ 81.25 MHz ≈ 706 clocks/bit
- **Memory map**: CPU base 0x80000000, ROM 0x80000000-0x80000FFF, RAM 0x80001000+, FB at end
- **Pipeline**: 3-stage, no hazard detection (insert NOPs manually)

## Next Steps

1. Draw something more interesting than a solid color (shapes, sprites, text)
2. Add game controller peripheral
3. Network peripheral (TBD)
