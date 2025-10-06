import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.constants import (
    OP_J_TYPE,

    PIPELINE_CYCLES,
)

wait_ns = 1

@cocotb.test()
async def test_jal_instruction(dut):
    """Test JAL instruction"""

    dest_register = 13
    start_address = 256
    magic_value = 0b11010101010111111111
    j_type_imm = 0b11111111111111111111110101010100
    expected_pc = start_address + j_type_imm
    expected_register_value = start_address + 4

    jal_instruction = OP_J_TYPE
    jal_instruction |= dest_register << 7 
    jal_instruction |= magic_value << 12

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = jal_instruction

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

    assert dut.cpu.r_PC.value.integer == expected_pc, f"JAL instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"
    assert dut.cpu.reg_file.Registers[dest_register].value.integer == expected_register_value, f"JAL instruction failed: Register x{dest_register} is {dut.cpu.reg_file.Registers[dest_register].value.integer:#010x}, expected {expected_register_value:#010x}"