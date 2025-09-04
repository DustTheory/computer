import cocotb
from cocotb.triggers import Timer
from cpu.utils import gen_r_type_instruction
from cpu.constants import OP_R_TYPE, FUNC3_ALU_XOR

wait_ns = 1

@cocotb.test()
async def test_xor_instruction(dut):
    """Test xor instruction"""
    tests = [
        (0x1, 0x2, 0x3),
        (0xF0F0F0F0, 0x0F0F0F0F, 0xFFFFFFFF),
        (0xFFFFFFFF, 0xFFFFFFFF, 0x0),
        (0x12345678, 0x87654321, 0x95511559),
        (0, 0, 0),
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    for rs1_value, rs2_value, expected_result in tests:
        instruction = gen_r_type_instruction(rd, FUNC3_ALU_XOR, rs1, rs2, 0)
        
        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.reg_file.Registers[rs2].value = rs2_value

        dut.cpu.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        
        assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"XOR instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
