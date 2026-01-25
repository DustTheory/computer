import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    send_unhalt_command,
    send_write_pc_command,
    wait_for_pipeline_flush,
    write_word_to_mem,
    write_half_to_mem,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,
    FUNC3_LS_H,
    PIPELINE_CYCLES,
    RAM_START_ADDR,
)

wait_ns = 1


@cocotb.test()
async def test_lh_instruction_when_equal(dut):
    """Test lh instruction"""

    rd = 5
    rs1 = 2
    start_address =  RAM_START_ADDR + 0
    mem_value = 0xBEEF

    offset = 0
    lh_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_H, rs1, offset)

    write_half_to_mem(dut.data_ram.mem, start_address, mem_value & 0xFFFF)
    write_word_to_mem(dut.instruction_ram.mem, RAM_START_ADDR + 0, lh_instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0

    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    dut.cpu.reg_file.Registers[rs1].value = start_address
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    result = dut.cpu.reg_file.Registers[rd].value.integer & 0xFFFF
    assert result == (mem_value & 0xFFFF), f"LH instruction failed: Rd value is {result:#010x}, expected {(mem_value & 0xFFFF):#010x}"

