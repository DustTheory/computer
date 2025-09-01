import cocotb
from cocotb.triggers import Timer
from cpu.constants import (
    ALU_SEL_ADD,
    ALU_SEL_SUB,
    ALU_SEL_AND,
    ALU_SEL_OR,
    ALU_SEL_XOR,
    ALU_SEL_SLL,
    ALU_SEL_SRL,
    ALU_SEL_SRA,
    ALU_SEL_UNKNOWN
)

wait_ns = 1


@cocotb.test()
async def addition_test(dut):

    tests = [
        (1, 1, 2),
        (2, 3, 5),
        (10, 15, 25),
        (0, 0, 0),
        (123, 456, 579),
        (-1, 1, 0),
        (-10, 1, -9),
        (-5, -5, -10),
        (0x7FFFFFFF , 1, -0x80000000),  # Overflow case
        (0xFFFFFFFF , 1, 0),  # Overflow case
        (-0x80000000 , -1, 0x7FFFFFFF)  # Underflow case
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_ADD

        await Timer(wait_ns, units="ns")

        result = dut.alu.o_Alu_Result.value.signed_integer
        assert result == expected, f"{a} + {b} should be {result}, got {expected}"

        
@cocotb.test()
async def subtraction_test(dut):
    
    tests = [
        (5, 3, 2),
        (10, 5, 5),
        (0, 0, 0),
        (100, 50, 50),
        (123, 456, -333),
        (-1, -1, 0),
        (-10, -5, -5),
        (-5, 5, -10),
        (0x80000000 , 1, 0x7FFFFFFF),  # Underflow case
        (0x00000000 , 1, -1),  # Underflow case
        (-0x80000000 , -1, -0x7FFFFFFF)  # Overflow case
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_SUB

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.signed_integer
        assert result == expected, f"{a} - {b} should be {expected}, got {result}"


@cocotb.test()
async def and_test(dut):
    
    tests = [
        (0b1100, 0b1010, 0b1000),
        (0b1111, 0b0000, 0b0000),
        (0b1010, 0b0101, 0b0000),
        (0b1111, 0b1111, 0b1111),
        (0xFFFFFFFF, 0x0F0F0F0F, 0x0F0F0F0F),
        (0x12345678, 0x87654321, 0x02244220)
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_AND

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.integer
        assert result == expected, f"{a:04b} AND {b:04b} should be {expected:04b}, got {result:04b}"


@cocotb.test()
async def or_test(dut):
    
    tests = [
        (0b1100, 0b1010, 0b1110),
        (0b1111, 0b0000, 0b1111),
        (0b1010, 0b0101, 0b1111),
        (0b0000, 0b0000, 0b0000),
        (0xFFFFFFFF, 0x0F0F0F0F, 0xFFFFFFFF),
        (0x12345678, 0x87654321, 0x97755779)
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_OR

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.integer
        assert result == expected, f"{a:04b} OR {b:04b} should be {expected:04b}, got {result:04b}"


@cocotb.test()
async def xor_test(dut):
    
    tests = [
        (0b1100, 0b1010, 0b0110),
        (0b1111, 0b0000, 0b1111),
        (0b1010, 0b0101, 0b1111),
        (0b0000, 0b0000, 0b0000),
        (0xFFFFFFFF, 0x0F0F0F0F, 0xF0F0F0F0),
        (0x12345678, 0x87654321, 0x95511559)
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_XOR

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.integer
        assert result == expected, f"{a:04b} XOR {b:04b} should be {expected:04b}, got {result:04b}"


@cocotb.test()
async def sll_test(dut):
    
    tests = [
        (0b0001, 1, 0b0010),
        (0b0001, 2, 0b0100),
        (0b0001, 3, 0b1000),
        (0x00000001, 31, 0x80000000),
        (0xFFFFFFFF, 4, 0xFFFFFFF0)
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_SLL

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.integer
        assert result == expected, f"{a} SLL {b} should be {expected}, got {result}"


@cocotb.test()
async def srl_test(dut):
    
    tests = [
        (0b1000, 1, 0b0100),
        (0b1000, 2, 0b0010),
        (0b1000, 3, 0b0001),
        (0b1000, 4, 0b0000),  # Shift out of range
        (0x80000000, 31, 0x00000001),
        (0xFFFFFFFF, 4, 0x0FFFFFFF)
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_SRL

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.integer
        assert result == expected, f"{a:04b} SRL {b} should be {expected:04b}, got {result:04b}"


@cocotb.test()
async def sra_test(dut):
    
    tests = [
        (0b1000, 1, 0b0100),
        (0b1000, 2, 0b0010),
        (0b1000, 3, 0b0001),
        (0b1000, 4, 0b0000),  # Shift out of range
        (0x80000000, 1, 0xC0000000),  # Sign bit should be preserved
        (0xFFFFFFFF, 4, 0xFFFFFFFF)  # All bits are 1
    ]

    for a, b, expected in tests:
        dut.alu.i_Input_A.value = a
        dut.alu.i_Input_B.value = b
        dut.alu.i_Alu_Select.value = ALU_SEL_SRA

        await Timer(wait_ns, units="ns")
        
        result = dut.alu.o_Alu_Result.value.integer
        assert result == expected, f"{a:04b} SRA {b} should be {expected:04b}, got {result:04b}"


@cocotb.test()
async def unknown_opcode_test(dut):
    
    dut.alu.i_Input_A.value = 5
    dut.alu.i_Input_B.value = 3
    dut.alu.i_Alu_Select.value = ALU_SEL_UNKNOWN
    await Timer(wait_ns, units="ns")
    result = dut.alu.o_Alu_Result.value.integer
    assert result == 0, f"Unknown opcode should result in 0, got {result}"
