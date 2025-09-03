import cocotb
from cocotb.triggers import Timer
from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,
    FUNC3_LS_BU
)

wait_ns = 1

@cocotb.test()
async def test_lbu_instruction(dut):
    """Test lbu instruction (unsigned byte load)"""
    start_address = 80
    rd = 7
    rs1 = 8
    rs1_value = 300
    mem_value = 0xAB
    offset = 12
    mem_address = rs1_value + offset
  
    lbu_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_BU, rs1, offset)
  
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = lbu_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.mem.Memory_Array[mem_address].value = mem_value
    dut.cpu.i_Clock.value = 0
  
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
  
    expected_value = mem_value  # Should be zero-extended
    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_value, f"LBU instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_value:#010x}"
