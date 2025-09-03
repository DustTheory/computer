import cocotb
from cocotb.triggers import Timer
from cpu.utils import gen_i_type_instruction
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_SLT

wait_ns = 1

@cocotb.test()
async def test_slti_instruction(dut):
    """Test slti instruction"""

    start_address = 0x0
    rs1 = 1
    rd = 3

    tests = [
        (1, 2, 1),
        (2, 1, 0),
        (-1, 1, 1),
        (1, -1, 0),
        (0, 0, 0),
        (-2, -1, 1),
        (-1, -2, 0),
    ]

    for rs1_value, imm_value, expected_result in tests:
        instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_SLT, rs1, imm_value)
      
        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.i_Clock.value = 0

        await Timer(wait_ns, units="ns")
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")

        assert dut.cpu.reg_file.Registers[rd].value == expected_result, f"SLTI instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value}, expected {expected_result}"