import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_i_type_instruction, send_unhalt_command, send_write_pc_command, write_word_to_mem, wait_for_pipeline_flush
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_SRL_SRA, PIPELINE_CYCLES, RAM_START_ADDR

wait_ns = 1

@cocotb.test()
async def test_srai_instruction(dut):
    """Test srai instruction"""

    tests = [
        # imm value is sign-extended, 12 bytes
        # (rs1_value, imm_value, expected_result)
        (0xFF, 4, 0XF),
        (0xAA, 2, 0x2A),
        (0xFFFFFFFF, 31, 0xFFFFFFFF),
        (0xFFFFFFFF, 1, 0XFFFFFFFF),
    ]

    start_address =  RAM_START_ADDR + 0x0
    rs1 = 1
    rd = 3

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    for rs1_value, imm_value, expected_result in tests:
        dut.i_Reset.value = 1
        await ClockCycles(dut.i_Clock, 1)
        dut.i_Reset.value = 0
        await ClockCycles(dut.i_Clock, 1)

        await send_write_pc_command(dut, start_address)
        await wait_for_pipeline_flush(dut)
        instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_SRL_SRA, rs1, imm_value | 0b0100000 << 5)
        write_word_to_mem(dut.instruction_ram.mem, start_address, instruction)
        dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF
        await send_unhalt_command(dut)  

        await ClockCycles(dut.i_Clock, PIPELINE_CYCLES + 3)

        actual = dut.cpu.reg_file.Registers[rd].value.integer
        assert actual == expected_result, (
            f"SRAI failed: rs1={rs1_value:#010x} imm={imm_value:#06x} -> rd={actual:#010x} expected={expected_result:#010x}"
        )
