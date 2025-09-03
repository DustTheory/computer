import cocotb
from cocotb.triggers import Timer
from cpu.utils import (
    gen_r_type_instruction,
)
from cpu.constants import (
    OP_R_TYPE,

    FUNC3_ALU_ADD_SUB
)

wait_ns = 1


@cocotb.test()
async def test_add_instruction(dut):
    """Test add instruction"""

    tests = [
        (0x1, 0x2, 0x3),  # 1 + 2 = 3
        (0x1234, 0x5678, 0x68AC),  # 0x1234 + 0x5678 = 0x68AC
        (0x7FFFFFFF , 1, -0x80000000),  # Overflow case
        (-1, 1, 0),  # -1 + 1 = 0
        (-2, -3, -5),  # -2 + -3 = -5
        (0, 0, 0),  # 0 + 0 = 0
        (0xFFFFFFFF, 0x1, 0x0),  # Wrap around case
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    for rs1_value, rs2_value, expected_result in tests:
        add_instruction = gen_r_type_instruction(OP_R_TYPE, rd, FUNC3_ALU_ADD_SUB, rs1, rs2, 0)

        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = add_instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.reg_file.Registers[rs2].value = rs2_value

        dut.cpu.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")

        assert dut.cpu.reg_file.Registers[rd].value.signed_integer == expected_result, f"ADD instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.signed_integer:#010x}, expected {expected_result:#010x}"






    
