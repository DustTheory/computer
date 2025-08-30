import cocotb
from cocotb.triggers import Timer

# Constants
CMP_SEL_BEQ = 0
CMP_SEL_BNE = 1
CMP_SEL_BLTU = 2
CMP_SEL_BGEU = 3
CMP_SEL_BLT = 4
CMP_SEL_BGE = 5
CMP_SEL_UNKNOWN = 6

wait_ns = 1


@cocotb.test()
async def beq_test(dut):

    tests = [
        (5, 5, 1),
        (10, 10, 1),
        (0, 0, 1),
        (100, 50, 0),
        (123, 456, 0),
        (-1, -1, 1),
        (-10, -10, 1),
        (-5, 5, 0),
        (0x7FFFFFFF , 0x7FFFFFFF, 1),
        (0xFFFFFFFF , 0xFFFFFFFF, 1),
        (-0x80000000 , -0x80000000, 1)  
    ]

    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BEQ

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} == {b} should be {expected}, got {result}"

        
@cocotb.test()
async def bne_test(dut):
    
    tests = [
        (5, 5, 0),
        (10, 10, 0),
        (0, 0, 0),
        (100, 50, 1),
        (123, 456, 1),
        (-1, -1, 0),
        (-10, -10, 0),
        (-5, 5, 1),
        (0x7FFFFFFF , 0x7FFFFFFF, 0),
        (0xFFFFFFFF , 0xFFFFFFFF, 0),
        (-0x80000000 , -0x80000000, 0)  
    ]

    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BNE

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} != {b} should be {expected}, got {result}"


@cocotb.test()
async def bltu_test(dut):
    
    tests = [
        (5, 10, 1),
        (10, 5, 0),
        (0, 0, 0),
        (100, 200, 1),
        (200, 100, 0),
        (0xFFFFFFFF , 0xFFFFFFFE, 0),
        (0xFFFFFFFE , 0xFFFFFFFF, 1),
        (0x7FFFFFFF , 0x80000000, 1),
        (0x80000000 , 0x7FFFFFFF, 0),
        (0x00000000 , 0xFFFFFFFF, 1),
        (0xFFFFFFFF , 0x00000000, 0)
    ]

    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BLTU

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} < {b} (unsigned) should be {expected}, got {result}"


@cocotb.test()
async def bgeu_test(dut):
    
    tests = [
        (5, 10, 0),
        (10, 5, 1),
        (0, 0, 1),
        (100, 200, 0),
        (200, 100, 1),
        (0xFFFFFFFF , 0xFFFFFFFE, 1),
        (0xFFFFFFFE , 0xFFFFFFFF, 0),
        (0x7FFFFFFF , 0x80000000, 0),
        (0x80000000 , 0x7FFFFFFF, 1),
        (0x00000000 , 0xFFFFFFFF, 0),
        (0xFFFFFFFF , 0x00000000, 1)
    ]

    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BGEU

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} >= {b} (unsigned) should be {expected}, got {result}"


@cocotb.test()
async def blt_test(dut):
    
    tests = [
        (5, 10, 1),
        (10, 5, 0),
        (0, 0, 0),
        (100, 200, 1),
        (200, 100, 0),
        (-10, -5, 1),
        (-5, -10, 0),
        (-1, 0, 1),
        (0, -1, 0),
        (-100, 100, 1),
        (100, -100, 0),
        (0x7FFFFFFF , -1, 0),
        (-1 , 0x7FFFFFFF, 1),
        (-0x80000000 , 0x7FFFFFFF, 1),
        (0x7FFFFFFF , -0x80000000, 0)
    ]

    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BLT

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} < {b} (signed) should be {expected}, got {result}"


@cocotb.test()
async def bge_test(dut):
    
    tests = [
        (5, 10, 0),
        (10, 5, 1),
        (0, 0, 1),
        (100, 200, 0),
        (200, 100, 1),
        (-10, -5, 0),
        (-5, -10, 1),
        (-1, 0, 0),
        (0, -1, 1),
        (-100, 100, 0),
        (100, -100, 1),
        (0x7FFFFFFF , -1, 1),
        (-1 , 0x7FFFFFFF, 0),
        (-0x80000000 , 0x7FFFFFFF, 0),
        (0x7FFFFFFF , -0x80000000, 1)
    ]

    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BGE

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} >= {b} (signed) should be {expected}, got {result}"


@cocotb.test()
async def unknown_test(dut):
    
    tests = [
        (5, 10),
        (10, 5),
        (0, 0),
        (100, 200),
        (200, 100),
        (-10, -5),
        (-5, -10),
        (-1, 0),
        (0, -1),
        (-100, 100),
        (100, -100),
        (0x7FFFFFFF , -1),
        (-1 , 0x7FFFFFFF),
        (-0x80000000 , 0x7FFFFFFF),
        (0x7FFFFFFF , -0x80000000)
    ]

    for a, b in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_UNKNOWN

        await Timer(wait_ns, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == 0, f"Unknown comparison should yield 0, got {result} for inputs {a}, {b}"
