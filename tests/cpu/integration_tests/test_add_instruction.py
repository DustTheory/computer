import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_r_type_instruction,
    write_word_to_mem,
)
from cpu.constants import (
    FUNC3_ALU_ADD_SUB,
    PIPELINE_CYCLES,
)

wait_ns = 1


@cocotb.test()
async def test_add_instruction(dut):
    """Test add instruction"""

    tests = [
        (0x1, 0x2, 0x3),  # 1 + 2 = 3
        (0x1234, 0x5678, 0x68AC),  # 0x1234 + 0x5678 = 0x68AC
        (0x7FFFFFFF , 1, -0x80000000),  # Overflow case
        (-1, 1, 0),  # -1 + 1 = 0
        (-2, -3, -5),  # -2 + -3 = -5
        (0, 0, 0),  # 0 + 0 = 0
        (0xFFFFFFFF, 0x1, 0x0),  # Wrap around case
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    add_instruction = gen_r_type_instruction(rd, FUNC3_ALU_ADD_SUB, rs1, rs2, 0)

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    for rs1_value, rs2_value, expected_result in tests:
        dut.cpu.i_Reset.value = 1
        await ClockCycles(dut.cpu.i_Clock, 1)
        dut.cpu.i_Reset.value = 0
        await ClockCycles(dut.cpu.i_Clock, 1)

        dut.cpu.r_PC.value = start_address
        write_word_to_mem(dut.cpu.instruction_memory.ram.mem, start_address, add_instruction)

        dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF
        dut.cpu.reg_file.Registers[rs2].value = rs2_value & 0xFFFFFFFF

        await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

        actual = dut.cpu.reg_file.Registers[rd].value.signed_integer
        assert actual == expected_result, (
            f"ADD failed: rs1={rs1_value:#010x} rs2={rs2_value:#010x} -> rd={actual:#010x} expected={expected_result:#010x}"
        )
    




    
