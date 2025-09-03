import cocotb
from cocotb.triggers import Timer
from cpu.utils import gen_r_type_instruction
from cpu.constants import OP_R_TYPE, FUNC3_ALU_SRL_SRA

wait_ns = 1

@cocotb.test()
async def test_sra_instruction(dut):
    """Test sra instruction"""
    tests = [
        (0x8, 1, 0x4),
        (-0xF0, 4, -0xF),
        (-0x80000000, 1, -0x40000000),
        (-1, 1, -1),
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    for rs1_value, rs2_value, expected_result in tests:
        instruction = gen_r_type_instruction(OP_R_TYPE, rd, FUNC3_ALU_SRL_SRA, rs1, rs2, 0b0100000)

        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.reg_file.Registers[rs2].value = rs2_value

        dut.cpu.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")

        assert dut.cpu.reg_file.Registers[rd].value.signed_integer == expected_result, f"SRA instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.signed_integer:#010x}, expected {expected_result:#010x}"
