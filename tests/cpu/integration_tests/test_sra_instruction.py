import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_r_type_instruction, send_unhalt_command, send_write_pc_command, write_word_to_mem, wait_for_pipeline_flush
from cpu.constants import FUNC3_ALU_SRL_SRA, PIPELINE_CYCLES, RAM_START_ADDR

wait_ns = 1

@cocotb.test()
async def test_sra_instruction(dut):
    """Test sra instruction"""
    tests = [
        (0x8, 1, 0x4),
        (-0xF0, 4, -0xF),
        (-0x80000000, 1, -0x40000000),
        (-1, 1, -1),
    ]

    start_address =  RAM_START_ADDR + 0x0
    rs1 = 1
    rs2 = 2
    rd  = 3
    
    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    sra_instruction = gen_r_type_instruction(rd, FUNC3_ALU_SRL_SRA, rs1, rs2, 0b0100000)

    for rs1_value, rs2_value, expected_result in tests:
        dut.i_Reset.value = 1
        await ClockCycles(dut.i_Clock, 1)
        dut.i_Reset.value = 0
        await ClockCycles(dut.i_Clock, 1)

        await send_write_pc_command(dut, start_address)
        await wait_for_pipeline_flush(dut)
        write_word_to_mem(dut.instruction_ram.mem, start_address, sra_instruction)
        dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF
        dut.cpu.reg_file.Registers[rs2].value = rs2_value & 0xFFFFFFFF
        await send_unhalt_command(dut)

        await ClockCycles(dut.i_Clock, PIPELINE_CYCLES + 3)

        actual = dut.cpu.reg_file.Registers[rd].value.signed_integer
        assert actual == expected_result, (
            f"SRA failed: rs1={rs1_value:#010x} rs2={rs2_value:#010x} -> rd={actual:#010x} expected={expected_result:#010x}"
        )
