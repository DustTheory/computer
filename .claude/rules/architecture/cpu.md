---
paths: hdl/cpu/**
---

# CPU Architecture

**Last updated**: 2026-01-05
**Sources**: [cpu.v](hdl/cpu/cpu.v), [cpu_core_params.vh](hdl/cpu/cpu_core_params.vh)

RV32I soft core, 3-stage pipeline. No M/F/D extensions, no multiplication.

## Pipeline Stages

**Stage 1: Fetch/Decode/Execute**
- Fetch instruction (AXI), decode, execute ALU/comparator
- Outputs: `w_Alu_Result`, `w_Compare_Result`, `w_Instruction_Valid`

**Stage 2: Memory/Wait**
- Issue AXI read/write for loads/stores
- Pipeline registers: `r_S2_*` (Valid, Alu_Result, Load_Data, Rd, Write_Enable)
- Stalls while memory operations complete

**Stage 3: Writeback**
- Write ALU result, load data, immediate, or PC+4 to register file
- Writeback mux selects source based on `r_S3_Wb_Src`

## Timing

**Cycles per instruction**: Variable
- S1: 1 cycle (ALU/decode)
- S2: 0 cycles (no memory) or 2-4 cycles (load/store AXI transaction)
- S3: 1 cycle (writeback)

Tests use `PIPELINE_CYCLES` from [tests/cpu/constants.py](tests/cpu/constants.py) as conservative wait.

## Stall Logic

```verilog
w_Stall_S1 = w_Debug_Stall
          || !i_Init_Calib_Complete
          || (r_S2_Valid && (w_S2_Is_Load || w_S2_Is_Store)
              && !(w_Mem_Read_Done || w_Mem_Write_Done));
```

CPU stalls when:
- `w_Debug_Stall`: Debug peripheral halted CPU
- `!i_Init_Calib_Complete`: DDR3 MIG not ready
- Memory op in progress: S2 has valid load/store waiting for AXI completion

## Hazards

**Status**: No hazard detection or forwarding implemented.

**Workaround**: Tests insert NOPs or wait `PIPELINE_CYCLES` between dependent instructions.

## PC (Program Counter)

**Normal**: `PC += 4` after instruction completes
**Branch taken**: `PC = PC + immediate`
**Jump**: `PC = target address`
**Reset**: `PC = 0`

Mux control: `w_Pc_Alu_Mux_Select` chooses between `PC+4` and `w_Alu_Result`

## Register File

32 registers × 32 bits (XLEN=32)
- Read ports: Rs1, Rs2 (from instruction[19:15], [24:20])
- Write port: Rd (r_S3_Rd), enabled by `w_Wb_Enable`
- Sources: ALU, comparator, immediate, PC+4, load data
- Register 0 always reads 0 (RISC-V spec)

See [register_file.v](hdl/cpu/register_file/register_file.v)

## Memory Interface

Two separate AXI4-Lite masters:
1. **Instruction memory**: Fetch-only (read)
2. **Data memory**: Loads/stores

No error handling - assumes all transactions succeed.

See [memory.md](memory.md) for AXI protocol details.
