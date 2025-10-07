import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_i_type_instruction, write_word_to_mem
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_AND, PIPELINE_CYCLES

wait_ns = 1

@cocotb.test()
async def test_andi_instruction(dut):
    """Test andi instruction"""

    tests = [
        # imm value is sign-extended, 12 bytes
        # (rs1_value, imm_value, expected_result)
        (0xFF, 0x0F, 0x0F),
        (0xAA, 0x55, 0x00),
        (0xFFFFFFFF, 0x0F0, 0x0F0),
    ]

    start_address = 0x0
    rs1 = 1
    rd = 3

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    for rs1_value, imm_value, expected_result in tests:
        dut.cpu.i_Reset.value = 1
        await ClockCycles(dut.cpu.i_Clock, 1)
        dut.cpu.i_Reset.value = 0
        await ClockCycles(dut.cpu.i_Clock, 1)

        instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_AND, rs1, imm_value)
        write_word_to_mem(dut.cpu.instruction_memory.ram.mem, start_address, instruction)
        dut.cpu.r_PC.value = start_address
        dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF

        await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

        actual = dut.cpu.reg_file.Registers[rd].value.integer
        assert actual == expected_result, (
            f"ANDI failed: rs1={rs1_value:#010x} imm={imm_value:#06x} -> rd={actual:#010x} expected={expected_result:#010x}"
        )
