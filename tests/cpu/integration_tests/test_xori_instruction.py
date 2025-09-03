import cocotb
from cocotb.triggers import Timer
from cpu.utils import gen_i_type_instruction
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_XOR

wait_ns = 1

@cocotb.test()
async def test_xori_instruction(dut):
    """Test xori instruction"""

    tests = [
        # imm value is sign-extended, 12 bytes
        # (rs1_value, imm_value, expected_result)
        (0xFF, 0x0F, 0xF0),
        (0xAA, 0x55, 0xFF),
        (0xFFFFFFFF, 0x0F0, 0xFFFFFF0F),
        (0xF0F0F0F0, 0x00F, 0xF0F0F0FF),
    ]

    start_address = 0x0
    rs1 = 1
    rd = 3

    for rs1_value, imm_value, expected_result in tests:
        instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_XOR, rs1, imm_value)

        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value

        dut.cpu.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        
        assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"XORI instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
