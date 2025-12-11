import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.constants import (
    OP_I_TYPE_ALU,

    FUNC3_BRANCH_BLT,
    FUNC3_ALU_ADD_SUB,
    
    ROM_BOUNDARY_ADDR,
)
from cpu.utils import (
    gen_i_type_instruction,
    gen_b_type_instruction,
    gen_r_type_instruction,
    write_instructions,
)

wait_ns = 1

@cocotb.test()
async def test_sum_loop(dut):
    """Test executing multiple instructions from instruction_memory"""
    dut._log.info("Starting multiple instruction fetch test")

    # Program that calculates sum of first 10 natural numbers
    instructions = [
        gen_i_type_instruction(OP_I_TYPE_ALU, 1, FUNC3_ALU_ADD_SUB, 0, 1), # addi $1, $0, 1 (i = 1)
        gen_i_type_instruction(OP_I_TYPE_ALU, 2, FUNC3_ALU_ADD_SUB, 0, 0), # addi $2, $0, 0 (sum = 0)
        gen_i_type_instruction(OP_I_TYPE_ALU, 3, FUNC3_ALU_ADD_SUB, 0, 11), # addi $3, $0, 10 (limit = 10)

        gen_r_type_instruction(2, FUNC3_ALU_ADD_SUB, 2, 1, 0), # addi $2, $2, 1 (sum += i)
        gen_i_type_instruction(OP_I_TYPE_ALU, 1, FUNC3_ALU_ADD_SUB, 1, 1), # addi $1, $1, 1 (i += 1)
        gen_b_type_instruction(FUNC3_BRANCH_BLT, 1, 3, -8), # beq $1, $3, loop (if i < limit, repeat)
        gen_i_type_instruction(OP_I_TYPE_ALU, 0, FUNC3_ALU_ADD_SUB, 0, 0), # addi $0, $0, 0 (nop)
    ]

    start_address =  ROM_BOUNDARY_ADDR + 0x0
    dut.cpu.r_PC.value = start_address
    write_instructions(dut.instruction_ram.mem, start_address, instructions)

    haltInstructions = 100
    endAddress = ROM_BOUNDARY_ADDR + len(instructions) * 4

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0

    while dut.cpu.r_PC.value.integer < endAddress and haltInstructions > 0:

        await ClockCycles(dut.i_Clock, 4)
        haltInstructions -= 1

    # After executing the program, $v0 should contain the sum of first 10 natural numbers
    expected_sum = sum(range(1, 11))  # 55
    actual_sum = dut.cpu.reg_file.Registers[2].value.integer  # $v0 is register 2
    assert actual_sum == expected_sum, f"Program execution failed: got sum {actual_sum}, expected {expected_sum}"
    dut._log.info("Multiple instruction fetch test completed successfully")