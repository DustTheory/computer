import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    send_unhalt_command,
    write_word_to_mem,
    write_byte_to_mem,
    send_write_pc_command,
    wait_for_pipeline_flush,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,
    FUNC3_LS_BU,
    PIPELINE_CYCLES,
    RAM_START_ADDR,
)

wait_ns = 1

@cocotb.test()
async def test_lbu_instruction(dut):
    """Test lbu instruction (unsigned byte load)"""

    rd = 5
    rs1 = 2
    start_address =  RAM_START_ADDR + 0
    rs1_value = 0
    offset = 0
    mem_value = 0xAB
    mem_address = rs1_value + offset

    lbu_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_BU, rs1, offset)
    write_byte_to_mem(dut.data_ram.mem, mem_address, mem_value & 0xFF)
    write_word_to_mem(dut.instruction_ram.mem, start_address, lbu_instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0

    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    result = dut.cpu.reg_file.Registers[rd].value.integer
    assert result == mem_value, f"LBU instruction failed: Rd value is {result:#010x}, expected {mem_value:#010x}"
