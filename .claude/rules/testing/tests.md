---
paths: tests/**
---

# Test Environment

**Last updated**: 2026-01-05
**Sources**: [Makefile](tests/Makefile), [utils.py](tests/cpu/utils.py), [constants.py](tests/cpu/constants.py)

cocotb (Python) + Verilator (C++) test framework for CPU verification.

## Running Tests

```bash
cd tests
source ./test_env/bin/activate  # CRITICAL: Activate venv first
make TEST_TYPE=unit             # Unit tests only
make TEST_TYPE=integration      # Integration tests only
make TEST_TYPE=all              # Both (cleans between runs)
make TEST_TYPE=integration TEST_FILE=test_add_instruction  # Single test
```

**Must activate venv** - tests fail with import errors otherwise.

## Test Types

**Unit tests** ([tests/cpu/unit_tests/](tests/cpu/unit_tests/)):
- Test individual modules (ALU, register file, control unit, memory)
- Harness: `cpu_unit_tests_harness.v`
- Examples: `test_arithmetic_logic_unit.py`, `test_comparator_unit.py`

**Integration tests** ([tests/cpu/integration_tests/](tests/cpu/integration_tests/)):
- Test full CPU instruction execution (fetch → decode → execute → writeback)
- Harness: `cpu_integration_tests_harness.v`
- Examples: `test_add_instruction.py`, `test_beq_instruction.py`, `test_lw_instruction.py`

## Common Test Pattern

```python
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cpu.utils import gen_r_type_instruction, write_instructions
from cpu.constants import *

@cocotb.test()
async def test_add_instruction(dut):
    """Test ADD R-type instruction"""

    # Start clock
    clock = Clock(dut.i_Clock, 1, "ns")
    cocotb.start_soon(clock.start())

    # Generate ADD instruction: rd=3, rs1=1, rs2=2
    add_instr = gen_r_type_instruction(
        rd=3, funct3=FUNC3_ALU_ADD_SUB, rs1=1, rs2=2, funct7=0
    )

    # Write to ROM
    write_instructions(dut.cpu.rom_memory, 0x0, [add_instr])

    # Set register values
    dut.cpu.register_file.registers[1].value = 5
    dut.cpu.register_file.registers[2].value = 3

    # Reset
    await reset_cpu(dut)

    # Wait for instruction completion
    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    # Verify result
    assert dut.cpu.register_file.registers[3].value == 8
```

## Utilities (tests/cpu/utils.py)

**Instruction generators** - create RISC-V instruction encodings:
- `gen_r_type_instruction(rd, funct3, rs1, rs2, funct7)` - R-type (ADD, SUB, AND, OR, XOR, SLT, shifts)
- `gen_i_type_instruction(opcode, rd, funct3, rs1, imm)` - I-type (ADDI, loads, JALR)
- `gen_s_type_instruction(funct3, rs1, rs2, imm)` - S-type (stores)
- `gen_b_type_instruction(funct3, rs1, rs2, offset)` - B-type (branches)
- `gen_u_type_instruction(opcode, rd, imm)` - U-type (LUI, AUIPC)
- `gen_j_type_instruction(rd, imm)` - J-type (JAL)

**Memory helpers**:
- `write_word_to_mem(mem_array, addr, value)` - 32-bit little-endian write
- `write_half_to_mem(mem_array, addr, value)` - 16-bit little-endian
- `write_byte_to_mem(mem_array, addr, value)` - 8-bit
- `write_instructions(mem_array, base_addr, instructions)` - Write instruction list
- `write_instructions_rom(mem_array, base_addr, instructions)` - ROM variant (word-indexed)

**UART helpers**:
- `uart_send_byte(clock, i_rx_serial, o_rx_dv, data_byte)` - Send byte over UART RX
- `uart_send_bytes(clock, i_rx_serial, o_rx_dv, byte_array)` - Send multiple bytes
- `uart_wait_for_byte(clock, i_tx_serial, o_tx_done)` - Receive byte from UART TX

**Reset/setup**:
- `reset_cpu(dut)` - Reset CPU and wait for DDR3 calibration
- `setup_cpu_test(dut)` - Clock + reset

## Constants (tests/cpu/constants.py)

**Don't duplicate constant values in docs** - reference the file instead.

**Contains**:
- Opcodes: `OP_R_TYPE`, `OP_I_TYPE`, `OP_LOAD`, `OP_STORE`, `OP_B_TYPE`, `OP_J_TYPE`, etc.
- Function codes: `FUNC3_ALU_ADD_SUB`, `FUNC3_BRANCH_BEQ`, etc.
- ALU selectors: `ALU_SEL_ADD`, `ALU_SEL_SUB`, `ALU_SEL_AND`, etc.
- Debug opcodes: `DEBUG_OP_HALT`, `DEBUG_OP_PING`, `DEBUG_OP_READ_PC`, etc.
- Timing: `CLOCK_FREQUENCY`, `UART_BAUD_RATE`, `UART_CLOCKS_PER_BIT`, `PIPELINE_CYCLES`
- Memory: `ROM_BOUNDARY_ADDR = 0x1000`

## UART Timing

**Baud rate**: 115200
**CPU clock**: 81.25 MHz (MIG ui_clk)
**Clocks per bit**: 81,250,000 / 115,200 ≈ **706 clocks**

Use `uart_send_byte()` / `uart_wait_for_byte()` from [utils.py](tests/cpu/utils.py) - timing handled internally.

## Makefile

**Auto-discovery**:
- Finds all `.v` and `.vh` files: `find $(SRC_DIR) -name "*.v" -o -name "*.vh"`
- Adds all subdirectories as Verilator include paths

**Key variables**:
- `SIM=verilator` - Simulator
- `TOPLEVEL` - Top-level module (set by TEST_TYPE)
- `MODULE` - Python test modules to run
- `VERILOG_SOURCES` - All Verilog files

## Debugging Tests

**Waveforms**: Verilator generates `.vcd` files - view with GTKWave
**Logging**: cocotb has built-in logging (`dut._log.info()`)
**ILA cores**: For FPGA debugging (not sim), see [arty-s7-50.xdc](config/arty-s7-50.xdc)

**Common issues**:
- Import errors: Activate venv (`source test_env/bin/activate`)
- Timing failures: Increase wait cycles (`PIPELINE_CYCLES` is conservative)
- UART failures: Check clock frequency matches constant (`81.25 MHz`)
