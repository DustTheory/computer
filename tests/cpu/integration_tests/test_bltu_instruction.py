import cocotb
from cocotb.triggers import Timer
from cpu.utils import (
    gen_b_type_instruction,
)
from cpu.constants import (
    FUNC3_BRANCH_BLTU
)

wait_ns = 1

@cocotb.test()
async def test_bltu_instruction_when_ltu(dut):
    """Test BLTU instruction: rs1 < rs2 (unsigned)"""
    start_address = 16
    rs1 = 2
    rs1_value = 0x100
    rs2 = 3
    rs2_value = 0xFFFFFFFF
    offset = 1024
    bltu_instruction = gen_b_type_instruction(FUNC3_BRANCH_BLTU, rs1, rs2, offset)
    expected_pc = start_address + offset
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = bltu_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
    assert dut.cpu.r_PC.value.integer == expected_pc, f"BLTU instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"

@cocotb.test()
async def test_bltu_instruction_when_geu(dut):
    """Test BLTU instruction: rs1 >= rs2 (unsigned)"""
    start_address = 16
    rs1 = 2
    rs1_value = 0xFFFFFFFF
    rs2 = 3
    rs2_value = 0x100
    offset = 1024
    bltu_instruction = gen_b_type_instruction(FUNC3_BRANCH_BLTU, rs1, rs2, offset)
    expected_pc = start_address + 4
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = bltu_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
    assert dut.cpu.r_PC.value.integer == expected_pc, f"BLTU instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"
