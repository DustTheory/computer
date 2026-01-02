# Memory Map

**Last updated**: 2026-01-02  
**Source files**: `hdl/cpu/memory/memory_axi.v`, `hdl/cpu/memory/memory.vh`  
**Related docs**: [cpu-architecture.md](cpu-architecture.md), [axi-interface.md](axi-interface.md)

---

Address space layout for the RISC-V CPU.

## Address Space Overview

| Region | Start | End | Size | Backing | Notes |
|--------|-------|-----|------|---------|-------|
| ROM | `0x0000` | `0x0FFF` | 4 KB | Block RAM | Read-only; bootstrap code |
| RAM | `0x1000` | (varies) | (varies) | DDR3 (MIG) | Read/write; main memory |
| Peripherals | TBD | TBD | TBD | Memory-mapped | Debug UART, future devices |

## ROM Region (`0x0000` - `0x0FFF`)

**Boundary**: `ROM_BOUNDARY_ADDR = 0x1000` (defined in `hdl/cpu/memory/memory.vh` and `tests/cpu/constants.py`)

**Implementation**: BRAM (Block RAM) inside FPGA, not DDR3

**Purpose**:
- Bootstrap code (initial PC = 0)
- Test programs loaded from `tests/rom.mem`
- Fast access (no AXI latency to external DRAM (Dynamic RAM))

**Access**: Read-only from CPU perspective (write during synthesis/bitstream generation)

**File**: `hdl/cpu/memory/memory_axi.v` handles ROM vs RAM routing

## RAM Region (`0x1000` - ?)

**Start**: `ROM_BOUNDARY_ADDR = 0x1000`

**End**: TBD (depends on DDR3 size; Arty S7-50 has 256 MB DDR3)

**Implementation**: DDR3 DRAM via Xilinx MIG (Memory Interface Generator)

**Purpose**:
- Stack
- Heap
- Data segment
- Framebuffer (future; VGA output)

**Access**: Read/write over AXI4-Lite

**Current status**: MIG calibration issues (blocker)

## Peripheral Region (Future)

**Not yet defined.** Candidates:
- Debug peripheral (UART)
- GPIO
- Timers
- Framebuffer control registers

**Typical RISC-V convention**: High addresses (e.g., `0xFFFF_xxxx`) or separate region above RAM

## Access Patterns

### Instruction Fetch

**Address**: Any (ROM or RAM)

**Interface**: `s_instruction_memory_axil_*` (AXI read-only)

**Behavior**:
- Read 32-bit word at `r_PC`
- If `< 0x1000`: Fast BRAM access
- If `>= 0x1000`: AXI transaction to DDR3

### Data Load/Store

**Address**: Any (typically RAM; ROM is read-only)

**Interface**: `s_data_memory_axil_*` (AXI read/write)

**Load/Store types**:
- `LW/SW`: 32-bit word
- `LH/LHU/SH`: 16-bit halfword (signed/unsigned)
- `LB/LBU/SB`: 8-bit byte (signed/unsigned)

**See**: `hdl/cpu/memory/memory.vh` for `LS_TYPE_*` constants

## Header Files Pattern

**Project convention**: Memory-related constants defined in `.vh` files alongside modules.

**Key files**:
- `hdl/cpu/memory/memory.vh` - Load/store types, state machine states, ROM boundary
- `hdl/cpu/cpu_core_params.vh` - Register widths, control signal widths
- `tests/cpu/constants.py` - Python mirror of `.vh` constants for test assertions

**Sync requirement**: Python constants must match Verilog `.vh` files. Update both when changing parameters.

## Memory Module State Machine

**File**: `hdl/cpu/memory/memory_axi.v`

**States** (from `memory.vh`):
- `IDLE` - Waiting for enable
- `READ_SUBMITTING` - Asserting `arvalid`, waiting for `arready`
- `READ_AWAITING` - Waiting for `rvalid` (data ready)
- `READ_SUCCESS` - Data received, return to IDLE
- `WRITE_SUBMITTING` - Asserting `awvalid`/`wvalid`, waiting for handshakes
- `WRITE_AWAITING` - Waiting for `bvalid` (write response)
- `WRITE_SUCCESS` - Write complete, return to IDLE

**Latency**: Variable; depends on AXI slave (BRAM (Block RAM) fast, DDR3 slow)

## Known Issues

- **Memory map incomplete**: RAM size and peripheral addresses TBD
- **No memory protection**: CPU can write to ROM region (AXI slave may ignore)
- **No alignment checks**: Misaligned loads/stores may behave unexpectedly
- **DDR3 not working**: MIG calibration issues prevent RAM access

## Next Steps

1. Resolve MIG calibration (current blocker)
2. Define RAM size based on DDR3 capacity (256 MB)
3. Allocate peripheral memory region
4. Add memory protection/alignment checks (optional)
