# CPU Architecture

**Last updated**: 2026-01-02  
**Source files**: `hdl/cpu/cpu.v`, `hdl/cpu/cpu_core_params.vh`  
**Related docs**: [memory-map.md](memory-map.md), [test-guide.md](test-guide.md), [axi-interface.md](axi-interface.md)

---

RISC-V RV32I soft core with 3-stage pipeline. No M/F/D extensions, no multiplication.

## Pipeline Stages

### Stage 1: Fetch/Decode/Execute
- **Fetch**: Read instruction from instruction memory (AXI)
- **Decode**: Control unit decodes instruction, generates control signals
- **Execute**: ALU/comparator operate on register file outputs
- **Registers**: `r_PC`, `w_Instruction`, control signals, ALU/comparator results

**Key signals out:**
- `w_Alu_Result` - ALU computation
- `w_Compare_Result` - Branch condition
- `w_Instruction_Valid` - Instruction ready

### Stage 2: Memory/Wait (S2)
- **Memory ops**: Issue AXI read/write transactions for loads/stores
- **Pipeline registers**: `r_S2_*` (Valid, Alu_Result, Load_Store_Type, Rd, Write_Enable, etc.)
- **Forwarding**: S2 results available for hazard detection (not yet implemented)

**Key signals:**
- `r_S2_Valid` - Stage active
- `r_S2_Alu_Result` - Carried from S1
- `r_S2_Load_Data` - Data from memory read

### Stage 3: Writeback (S3)
- **Register write**: Write ALU result, load data, immediate, or PC+4 to register file
- **Pipeline registers**: `r_S3_*` (mirrors S2 structure)
- **Writeback mux**: `w_Wb_Data` selects source based on `r_S3_Wb_Src`

**Key signals:**
- `w_Wb_Enable` - Triggers register file write
- `w_Wb_Data` - Data to write to Rd

## Pipeline Timing

**Cycles per instruction**: Variable, depends on memory operations

**Instruction flow**:
- Stage 1 (Fetch/Decode/Execute): 1 cycle to generate ALU result and control signals
- Stage 2 (Memory/Wait): Stalls dynamically while memory operations complete
  - No memory op: Passes through immediately
  - Load/Store: Waits for AXI transaction (typically 2-4 cycles)
- Stage 3 (Writeback): 1 cycle to write result to register file

**Test wait time**: Integration tests use `PIPELINE_CYCLES` (from `tests/cpu/constants.py`) as a conservative wait, but actual execution time varies per instruction type.

**Stall logic** (from `cpu.v`):
```verilog
w_Stall_S1 = w_Debug_Stall 
          || !i_Init_Calib_Complete 
          || (r_S2_Valid && (w_S2_Is_Load || w_S2_Is_Store) 
              && !(w_Mem_Read_Done || w_Mem_Write_Done));
```

**CPU stalls when**:
- `w_Debug_Stall`: Debug peripheral has halted CPU
- `!i_Init_Calib_Complete`: DDR3 MIG not initialized yet
- Memory operation in progress: Stage 2 has valid load/store waiting for AXI completion

**Effect**: When stalled, Stage 1→Stage 2 and Stage 2→Stage 3 register updates are blocked. Pipeline waits until memory transaction completes (`READ_SUCCESS` or `WRITE_SUCCESS` state).

## Hazard Handling

**Current status**: No hazard detection or forwarding implemented.

**Behavior**:
- RAW (Read-After-Write): Pipeline may produce incorrect results if dependent instructions are too close
- Control hazards: Branches/jumps update PC; pipeline does not flush automatically
- Test workaround: Tests insert NOPs or wait full `PIPELINE_CYCLES` between dependent instructions

**Future**: Add forwarding paths from S2/S3 back to S1 ALU inputs.

## PC (Program Counter) Behavior

**PC increment**: `w_PC_Next = r_PC + 4` (word-aligned)

**PC update**:
- Normal: PC += 4 after instruction completes
- Branch taken: PC = ALU result (PC + immediate)
- Jump (JAL/JALR): PC = target address
- Reset: PC = 0 (or initial value)

**Mux control**: `w_Pc_Alu_Mux_Select` chooses between `w_PC_Next` and `w_Alu_Result`

## Register File

**Size**: 32 registers × 32 bits (`XLEN=32`)

**Access**:
- Read ports: Rs1 (`w_Rs_1 = w_Instruction[19:15]`), Rs2 (`w_Rs_2 = w_Instruction[24:20]`)
- Write port: Rd (`r_S3_Rd`), enabled by `w_Wb_Enable`
- Write sources: ALU, comparator, immediate, PC+4, memory load

**Register 0**: Always reads as 0 (RISC-V spec compliance assumed; verify in `register_file.v`)

## Memory Interface (AXI4-Lite)

**Two separate AXI masters**:
1. **Instruction memory**: Fetch-only (read transactions)
2. **Data memory**: Loads and stores

**Protocol**: AXI4-Lite (simplified, no burst support)

**Error handling**: None. Assumes all transactions succeed; no timeout logic.

**Address width**: 32 bits

## Known Issues

- **No hazard detection**: Dependent instructions must be separated by sufficient cycles (tests use conservative `PIPELINE_CYCLES` wait)
- **No error handling**: AXI failures (bresp != 0) are ignored
- **No pipeline flush**: Branches may execute wrong-path instructions
- **Variable latency**: Execution time depends on memory operations, no optimization for cache hits

## File Locations

- **Pipeline**: `hdl/cpu/cpu.v` (lines 50-200 for stage definitions)
- **Parameters**: `hdl/cpu/cpu_core_params.vh`
- **Test constants**: `tests/cpu/constants.py`
- **Register file**: `hdl/cpu/register_file/register_file.v`
- **Control unit**: `hdl/cpu/control_unit/control_unit.v`
