import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_i_type_instruction, write_word_to_mem
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_SLT, PIPELINE_CYCLES

wait_ns = 1

@cocotb.test()
async def test_slti_instruction(dut):
    """Test slti instruction"""

    start_address = 0x0
    rs1 = 1
    rd = 3

    tests = [
        (1, 2, 1),
        (2, 1, 0),
        (-1, 1, 1),
        (1, -1, 0),
        (0, 0, 0),
        (-2, -1, 1),
        (-1, -2, 0),
    ]

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    for rs1_value, imm_value, expected_result in tests:
        instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_SLT, rs1, imm_value)

        # Reset
        dut.cpu.i_Reset.value = 1
        await ClockCycles(dut.cpu.i_Clock, 1)
        dut.cpu.i_Reset.value = 0
        await ClockCycles(dut.cpu.i_Clock, 1)

        write_word_to_mem(dut.cpu.instruction_memory.ram.mem, start_address, instruction)
        dut.cpu.r_PC.value = start_address
        dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF

        await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

        actual = dut.cpu.reg_file.Registers[rd].value.integer
        assert actual == expected_result, f"SLTI failed: rs1={rs1_value:#010x} imm={imm_value:#06x} -> rd={actual} expected={expected_result}"