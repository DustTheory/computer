import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_s_type_instruction,
    write_word_to_mem,
)
from cpu.constants import (
    FUNC3_LS_H,

    PIPELINE_CYCLES,
)

wait_ns = 1

@cocotb.test()
async def test_sh_instruction(dut):
    """Test sh instruction"""
    start_address = 0x40
    rs1 = 0x4
    rs2 = 0x5
    rs1_value = 0
    rs2_value = 0xBEEF
    imm_value = 0
    mem_address = rs1_value + imm_value
    low_byte_addr  = mem_address
    high_byte_addr = mem_address + 1

    sh_instruction = gen_s_type_instruction(FUNC3_LS_H, rs1, rs2, imm_value)
   
    dut.cpu.r_PC.value = start_address
    write_word_to_mem(dut.cpu.instruction_memory.ram.mem, start_address, sh_instruction)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

    expected_low  = rs2_value & 0xFF
    expected_high = (rs2_value >> 8) & 0xFF
    assert dut.cpu.mem.ram.mem[low_byte_addr].value == expected_low, f"SH instruction failed: low byte {low_byte_addr} is {dut.cpu.mem.ram.mem[low_byte_addr].value.integer:#04x}, expected {expected_low:#04x}"
    assert dut.cpu.mem.ram.mem[high_byte_addr].value == expected_high, f"SH instruction failed: high byte {high_byte_addr} is {dut.cpu.mem.ram.mem[high_byte_addr].value.integer:#04x}, expected {expected_high:#04x}"