# Test Guide

**Last updated**: 2026-01-02  
**Source files**: `tests/Makefile`, `tests/cpu/constants.py`, `tests/cpu/utils.py`  
**Related docs**: [cpu-architecture.md](cpu-architecture.md), [memory-map.md](memory-map.md)

---

How to run, write, and debug tests for the RISC-V CPU.

## Running Tests

### All Tests
```bash
cd tests && make
```

### Unit Tests Only
```bash
cd tests && make TEST_TYPE="unit"
```

### Integration Tests Only
```bash
cd tests && make TEST_TYPE="integration"
```

### Single Test File
```bash
cd tests && make TEST_TYPE="integration" TEST_FILE="test_add_instruction"
```

## Test Infrastructure

**Framework**: cocotb (Python-based Verilog/VHDL testbench)

**Simulator**: Verilator (fast, open-source)

**Test location**:
- Unit: `tests/cpu/unit_tests/`
- Integration: `tests/cpu/integration_tests/`

**Harness files**:
- `cpu_unit_tests_harness.v` - Top-level for unit tests
- `cpu_integration_tests_harness.v` - Top-level for integration tests

## Test Structure

### Unit Tests

**Purpose**: Test individual modules in isolation

**Examples**:
- `test_arithmetic_logic_unit.py` - ALU operations (ADD, SUB, AND, OR, XOR, shifts, SLT)
- `test_comparator_unit.py` - Branch conditions (EQ, NE, LT, GE, LTU, GEU)
- `test_register_file.py` - Register read/write
- `test_memory_axi.py` - Memory load/store over AXI

**Pattern**:
```python
@cocotb.test()
async def test_alu_add(dut):
    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Enable.value = 1
    dut.i_Input_A.value = 5
    dut.i_Input_B.value = 3
    dut.i_Alu_Select.value = ALU_SEL_ADD
    
    await ClockCycles(dut.i_Clock, 1)
    
    assert dut.o_Alu_Result.value == 8
```

### Integration Tests

**Purpose**: Test full CPU instruction execution (fetch → decode → execute → writeback)

**Examples**:
- `test_add_instruction.py` - ADD R-type instruction
- `test_beq_instruction.py` - BEQ branch
- `test_lw_instruction.py` - Load word from memory

**Pattern**:
```python
@cocotb.test()
async def test_add_instruction(dut):
    tests = [
        (0x1, 0x2, 0x3),  # 1 + 2 = 3
        (0x7FFFFFFF, 1, -0x80000000),  # Overflow
    ]
    
    start_address = ROM_BOUNDARY_ADDR + 0x0
    rs1, rs2, rd = 1, 2, 3
    
    add_instruction = gen_r_type_instruction(rd, FUNC3_ALU_ADD_SUB, rs1, rs2, 0)
    
    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())
    
    for rs1_val, rs2_val, expected in tests:
        dut.i_Reset.value = 1
        await ClockCycles(dut.i_Clock, 1)
        dut.i_Reset.value = 0
        
        dut.cpu.r_PC.value = start_address
        write_word_to_mem(dut.instruction_ram.mem, start_address, add_instruction)
        
        dut.cpu.reg_file.Registers[rs1].value = rs1_val
        dut.cpu.reg_file.Registers[rs2].value = rs2_val
        
        await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)
        
        actual = dut.cpu.reg_file.Registers[rd].value.signed_integer
        assert actual == expected, f"ADD failed: {rs1_val:#x} + {rs2_val:#x} = {actual:#x}, expected {expected:#x}"
```

## Test Utilities

**File**: `tests/cpu/utils.py`

**Key functions**:
- `gen_r_type_instruction(rd, func3, rs1, rs2, func7)` - Generate R-type instruction
- `gen_i_type_instruction(rd, func3, rs1, imm)` - Generate I-type
- `gen_s_type_instruction(func3, rs1, rs2, imm)` - Generate S-type
- `gen_b_type_instruction(func3, rs1, rs2, imm)` - Generate B-type
- `gen_u_type_instruction(rd, imm)` - Generate U-type
- `gen_j_type_instruction(rd, imm)` - Generate J-type
- `write_word_to_mem(mem, addr, data)` - Write 32-bit word to test memory

## Test Constants

**File**: `tests/cpu/constants.py`

**Key constants**:
- `PIPELINE_CYCLES` - Conservative wait time for integration tests (instruction execution is actually variable due to dynamic stalls)
- `ROM_BOUNDARY_ADDR` - Address split between ROM and RAM regions
- `ALU_SEL_*`, `CMP_SEL_*`, `IMM_*`, `LS_TYPE_*` - Mirrors `.vh` files
- `OP_*`, `FUNC3_*` - RISC-V opcodes and function codes
- `UART_BAUD_RATE`, `UART_CLOCKS_PER_BIT` - UART timing parameters

**Sync requirement**: Must match Verilog `.vh` files. Update both when changing HDL.

## Writing New Tests

### Unit Test Template
```python
import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

@cocotb.test()
async def test_my_module(dut):
    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())
    
    # Setup
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    
    # Test
    dut.i_Enable.value = 1
    dut.some_input.value = test_value
    await ClockCycles(dut.i_Clock, 1)
    
    # Assert
    assert dut.some_output.value == expected_value
```

### Integration Test Template
```python
from cpu.utils import gen_r_type_instruction, write_word_to_mem
from cpu.constants import PIPELINE_CYCLES, ROM_BOUNDARY_ADDR

@cocotb.test()
async def test_my_instruction(dut):
    instruction = gen_r_type_instruction(rd=3, func3=0, rs1=1, rs2=2, func7=0)
    start_address = ROM_BOUNDARY_ADDR
    
    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())
    
    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    
    dut.cpu.r_PC.value = start_address
    write_word_to_mem(dut.instruction_ram.mem, start_address, instruction)
    
    dut.cpu.reg_file.Registers[1].value = input1
    dut.cpu.reg_file.Registers[2].value = input2
    
    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)
    
    actual = dut.cpu.reg_file.Registers[3].value
    assert actual == expected
```

## Debugging Failed Tests

### Check test output
```bash
cd tests && make TEST_TYPE="unit" TEST_FILE="test_alu" 2>&1 | tee test.log
```

### Verilator waveforms
Edit `tests/Makefile` to add:
```makefile
EXTRA_ARGS += --trace --trace-structs
```
Then view `sim_build/dump.vcd` in GTKWave.

### Print DUT signals
```python
print(f"PC={dut.cpu.r_PC.value:#x}")
print(f"Instruction={dut.cpu.w_Instruction.value:#x}")
```

### Common issues
- **Timing**: Not waiting long enough for instruction completion (use `PIPELINE_CYCLES` as safe default)
- **Reset**: Forgot to pulse reset before test
- **Constants mismatch**: Python constants don't match `.vh` files
- **Signed vs unsigned**: Use `.signed_integer` for signed results
- **Memory latency**: Integration tests may need more cycles if AXI memory is slow

## Current Test Status

**All tests passing** (as of last run)

**Coverage**:
- ✓ All RV32I instructions (except ECALL/EBREAK)
- ✓ All ALU operations
- ✓ All branch conditions
- ✓ All load/store types
- ✓ Debug peripheral halt/reset
- ✓ UART transmit/receive

**Missing**:
- ⚠ Hazard detection tests (not implemented in HDL)
- ⚠ AXI error handling (not implemented)
- ⚠ DDR3 integration tests (blocked on MIG)

## Makefile Targets

**File**: `tests/Makefile`

**Variables**:
- `TEST_TYPE` - "unit" or "integration" (default: both)
- `TEST_FILE` - Specific test file name (default: all)
- `SIM` - Simulator to use (default: verilator)

**Internally**:
- Finds all `.v` and `.vh` files in `hdl/` and `hdl_inc/`
- Sets up Verilator include paths
- Runs cocotb with specified test modules
