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

    # input [XLEN-1:0] i_Input_A,
    # input [XLEN-1:0] i_Input_B,
    # input [CMP_SEL_WIDTH:0] i_Compare_Select,
    # output reg o_Cmp_Result
    for a, b, expected in tests:
        dut.comparator_unit.i_Input_A.value = a
        dut.comparator_unit.i_Input_B.value = b
        dut.comparator_unit.i_Compare_Select.value = CMP_SEL_BEQ

        await Timer(10, units="ns")

        result = dut.comparator_unit.o_Compare_Result.value.integer
        assert result == expected, f"{a} == {b} should be {expected}, got {result}"
        
