import cocotb
from cocotb.triggers import Timer
from cpu.utils import gen_r_type_instruction
from cpu.constants import OP_R_TYPE, FUNC3_ALU_SLTU

wait_ns = 1

@cocotb.test()
async def test_sltu_instruction(dut):
    """Test sltu instruction"""
    tests = [
        (1, 2, 1),
        (2, 1, 0),
        (0xFFFFFFFF, 0, 0),
        (0, 0xFFFFFFFF, 1),
        (0, 0, 0),
        (0x7FFFFFFF, 0x80000000, 1),
        (0x80000000, 0x7FFFFFFF, 0),
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3
    
    for rs1_value, rs2_value, expected_result in tests:
        instruction = gen_r_type_instruction(rd, FUNC3_ALU_SLTU, rs1, rs2, 0)

        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.reg_file.Registers[rs2].value = rs2_value

        dut.cpu.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        
        assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"SLTU instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer}, expected {expected_result}"
