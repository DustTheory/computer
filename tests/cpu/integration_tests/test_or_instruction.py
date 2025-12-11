import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_r_type_instruction, write_word_to_mem
from cpu.constants import FUNC3_ALU_OR, PIPELINE_CYCLES, ROM_BOUNDARY_ADDR

wait_ns = 1

@cocotb.test()
async def test_or_instruction(dut):
    """Test or instruction"""
    tests = [
        (0x1, 0x2, 0x3),
        (0xF0F0F0F0, 0x0F0F0F0F, 0xFFFFFFFF),
        (0xFFFFFFFF, 0x0, 0xFFFFFFFF),
        (0x12345678, 0x87654321, 0x97755779),
        (0, 0, 0),
    ]

    start_address =  ROM_BOUNDARY_ADDR + 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    for rs1_value, rs2_value, expected_result in tests:
        instruction = gen_r_type_instruction(rd, FUNC3_ALU_OR, rs1, rs2, 0)

        # Reset per test case
        dut.i_Reset.value = 1
        await ClockCycles(dut.i_Clock, 1)
        dut.i_Reset.value = 0
        await ClockCycles(dut.i_Clock, 1)

        write_word_to_mem(dut.instruction_ram.mem, start_address, instruction)
        dut.cpu.r_PC.value = start_address
        dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF
        dut.cpu.reg_file.Registers[rs2].value = rs2_value & 0xFFFFFFFF

        await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

        actual = dut.cpu.reg_file.Registers[rd].value.integer
        assert actual == expected_result, f"OR failed: rs1={rs1_value:#010x} rs2={rs2_value:#010x} -> rd={actual:#010x} expected={expected_result:#010x}"
