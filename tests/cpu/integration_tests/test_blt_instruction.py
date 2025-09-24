import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_b_type_instruction,
)
from cpu.constants import (
    FUNC3_BRANCH_BLT
)

wait_ns = 1

@cocotb.test()
async def test_blt_instruction_when_lt(dut):
    """Test BLT instruction: rs1 < rs2"""
    start_address = 16
    rs1 = 2
    rs1_value = 0x100
    rs2 = 3
    rs2_value = 0x200
    offset = 1024
    blt_instruction = gen_b_type_instruction(FUNC3_BRANCH_BLT, rs1, rs2, offset)
    expected_pc = start_address + offset
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = blt_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)

    assert dut.cpu.r_PC.value.integer == expected_pc, f"BLT instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"

@cocotb.test()
async def test_blt_instruction_when_ge(dut):
    """Test BLT instruction: rs1 >= rs2"""
    start_address = 16
    rs1 = 2
    rs1_value = 0x200
    rs2 = 3
    rs2_value = 0x100
    offset = 1024
    blt_instruction = gen_b_type_instruction(FUNC3_BRANCH_BLT, rs1, rs2, offset)
    expected_pc = start_address + 4
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = blt_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)
    
    assert dut.cpu.r_PC.value.integer == expected_pc, f"BLT instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"
