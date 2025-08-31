import cocotb
from cocotb.triggers import Timer
from constants import (
    IMM_U_TYPE,
    IMM_B_TYPE,
    IMM_I_TYPE,
    IMM_J_TYPE,
    IMM_S_TYPE,
    IMM_UNKNOWN_TYPE
)

wait_ns = 1


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
        
        await Timer(wait_ns, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"U-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"


@cocotb.test()
async def b_type_test(dut):
    # abcdefg0000000000000uvwxy -> aaaaaaaaaaaaaaaaaaaaybcdefguvwx0
    tests = [
        (0x0, 0x0),
        (0b0111111000000000000011111, 0b00000000000000000000111111111110),
        (0b1111111000000000000011111, 0b11111111111111111111111111111110),
        (0b0101010000000000000010101, 0b00000000000000000000110101010100),
    ]
    
    for instr, expected in tests:
        dut.immediate_unit.i_Imm_Select.value = IMM_B_TYPE
        dut.immediate_unit.i_Instruction_No_Opcode.value = instr
        
        await Timer(wait_ns, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"B-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"


@cocotb.test()
async def i_type_test(dut):

    # abcdefghijkl0000000000000 -> aaaaaaaaaaaaaaaaaaaaabcdefghijkl    
    tests = [
        (0x0, 0x0),
        (0b1111111111110000000000000, 0b11111111111111111111111111111111),
        (0b0111111111110000000000000, 0b00000000000000000000011111111111),
        (0b0101010101010000000000000, 0b00000000000000000000010101010101),
    ]

    for instr, expected in tests:
        dut.immediate_unit.i_Imm_Select.value = IMM_I_TYPE
        dut.immediate_unit.i_Instruction_No_Opcode.value = instr
        
        await Timer(wait_ns, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"I-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"

        
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
        
        await Timer(wait_ns, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"J-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"


@cocotb.test()
async def s_type_test(dut):

    # abcdefg0000000000000uvwxy -> aaaaaaaaaaaaaaaaaaaaabcdefguvwxy
    tests = [
        (0x0, 0x0),
         # abcdefg0000000000000uvwxy -> aaaaaaaaaaaaaaaaaaaaabcdefguvwxy
        (0b0111111000000000000011111, 0b00000000000000000000011111111111),
        (0b1111111000000000000011111, 0b11111111111111111111111111111111),
        (0b1010101000000000000010101, 0b11111111111111111111101010110101),
    ]

    for instr, expected in tests:
        dut.immediate_unit.i_Imm_Select.value = IMM_S_TYPE
        dut.immediate_unit.i_Instruction_No_Opcode.value = instr
        
        await Timer(wait_ns, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"S-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"

        
@cocotb.test()
async def unknown_type_test(dut):
    
    tests = [
        (0x0, 0x0),
        (0b0111111000000000000011111, 0x0),
        (0b1111111000000000000011111, 0x0),
        (0b1010101000000000000010101, 0x0),
    ]

    for instr, expected in tests:
        dut.immediate_unit.i_Imm_Select.value = IMM_UNKNOWN_TYPE
        dut.immediate_unit.i_Instruction_No_Opcode.value = instr
        
        await Timer(wait_ns, units="ns")
        result = dut.immediate_unit.o_Immediate.value.integer
        assert result == expected, f"Unknown-type immediate for instruction {instr:#b} should be {expected:#b}, got {result:#b}"
