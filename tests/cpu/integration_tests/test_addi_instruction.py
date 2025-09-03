import cocotb
from cocotb.triggers import Timer
from cpu.utils import gen_i_type_instruction
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_ADD_SUB

wait_ns = 1

@cocotb.test()
async def test_addi_instruction(dut):
    """Test addi instruction"""

    start_address = 0x0
    rs1 = 1
    rs1_value = 0x20
    rd = 3
    imm_value = 0x10
    expected_result = rs1_value + imm_value

    instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_ADD_SUB, rs1, imm_value)

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value

    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
    
    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"ADD instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
