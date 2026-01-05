---
paths:
  - hdl/cpu/memory/**
  - hdl/cpu/instruction_memory/**
---

# Memory Architecture

**Last updated**: 2026-01-05
**Sources**: [memory_axi.v](hdl/cpu/memory/memory_axi.v), [memory.vh](hdl/cpu/memory/memory.vh)

AXI4-Lite memory interface for CPU instruction/data access.

## Memory Map

| Region | Start | End | Size | Backing | Notes |
|--------|-------|-----|------|---------|-------|
| ROM | `0x0000` | `0x0FFF` | 4 KB | BRAM | Bootstrap, read-only |
| RAM | `0x1000` | (varies) | 256 MB | DDR3 (MIG) | Main memory, stack, heap |
| Peripherals | TBD | TBD | TBD | Memory-mapped | Debug UART (future) |

**ROM boundary**: `ROM_BOUNDARY_ADDR = 0x1000` - see [memory.vh](hdl/cpu/memory/memory.vh) and [tests/cpu/constants.py](tests/cpu/constants.py)

## AXI State Machine

**States**: `IDLE` → `READ_SUBMITTING` → `READ_AWAITING` → `READ_SUCCESS`
**Write**: `IDLE` → `WRITE_SUBMITTING` → `WRITE_AWAITING` → `WRITE_SUCCESS`

**Latency**: 2-4 cycles (BRAM fast, DDR3 slower)

## Load/Store Types

**Supported**:
- `LW/SW`: 32-bit word
- `LH/LHU/SH`: 16-bit halfword (signed/unsigned)
- `LB/LBU/SB`: 8-bit byte (signed/unsigned)

**Byte alignment**: AXI write strobes (`wstrb`) enable byte-level writes without read-modify-write. Load data extraction uses `i_Addr[1:0]` offset with sign-extension for LB/LH.

See [memory_axi.v](hdl/cpu/memory/memory_axi.v) for alignment logic.

## Access Patterns

**Instruction fetch**:
- Address < 0x1000: Fast BRAM access
- Address >= 0x1000: AXI transaction to DDR3
- Interface: `s_instruction_memory_axil_*` (read-only)

**Data load/store**:
- Typically RAM (ROM is read-only)
- Interface: `s_data_memory_axil_*` (read/write)

## Constants

Constants defined in `.vh` files:
- [memory.vh](hdl/cpu/memory/memory.vh): `LS_TYPE_*`, state machine states, ROM boundary
- [cpu_core_params.vh](hdl/cpu/cpu_core_params.vh): Register widths, control signal widths

Python mirror: [tests/cpu/constants.py](tests/cpu/constants.py) - must stay in sync with `.vh` files.

## Current Status

- DDR3 operational @ 81.25 MHz (MIG initialized 2026-01-04)
- No memory protection (CPU can write to ROM, slave may ignore)
- No alignment checks (misaligned loads/stores may behave unexpectedly)
