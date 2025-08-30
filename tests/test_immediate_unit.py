import cocotb
from cocotb.triggers import Timer

# Constants
IMM_U_TYPE = 0
IMM_B_TYPE = 1
IMM_I_TYPE = 2
IMM_J_TYPE = 3
IMM_S_TYPE = 4
IMM_UNKNOWN_TYPE = 5


@cocotb.test()
async def u_type_test(dut):

    tests = [
        (0x0, 0x0),
        (0b0000100000, 0b00001000000000000),
        (0b0000011111, 0b00000000000000000),
        (0b1111100000, 0b11111000000000000),
    ]

    for instr, expected in tests:
        dut.immediate_unit.i_Imm_Select.value = IMM_U_TYPE
        dut.immediate_unit.i_Instruction_No_Opcode.value = instr
        await Timer(10, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"U-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"

        
@cocotb.test()
async def j_type_test(dut):

    # abcdefghijklmnopqrst00000 -> aaaaaaaaaaaamnopqrstlbcdefghijk0    
    tests = [
        (0x0, 0x0),
        (0b0000000000001111111100000, 0b00000000000011111111000000000000),
        (0b1000000000001111111100000, 0b11111111111111111111000000000000),
        (0b1101010101011111111100000, 0b11111111111111111111110101010100),
    ]

    for instr, expected in tests:
        dut.immediate_unit.i_Imm_Select.value = IMM_J_TYPE
        dut.immediate_unit.i_Instruction_No_Opcode.value = instr
        await Timer(10, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"J-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"
