import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,
    FUNC3_LS_HU
)

wait_ns = 1

@cocotb.test()
async def test_lhu_instruction(dut):
    """Test lhu instruction (unsigned halfword load)"""
    start_address = 96
    rd = 9
    rs1 = 10
    rs1_value = 400
    mem_value = 0xBEEF
    offset = 16
    mem_address = rs1_value + offset
    
    lhu_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_HU, rs1, offset)
    
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = lhu_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.mem.Memory_Array[mem_address].value = mem_value & 0xFF
    dut.cpu.mem.Memory_Array[mem_address + 1].value = (mem_value >> 8) & 0xFF

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)

    expected_value = mem_value  # Should be zero-extended
    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_value, f"LHU instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_value:#010x}"
