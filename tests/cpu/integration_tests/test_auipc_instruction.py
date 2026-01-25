import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.constants import (
    OP_U_TYPE_AUIPC,

    PIPELINE_CYCLES,

    RAM_START_ADDR,
    DEBUG_OP_HALT,
    DEBUG_OP_UNHALT,
)
from cpu.utils import send_unhalt_command, send_write_pc_command, write_word_to_mem, uart_send_byte, wait_for_pipeline_flush

wait_ns = 1

@cocotb.test()
async def test_auipc_instruction(dut):
    """Test AUIPC instruction"""

    dest_register = 22
    start_address =  RAM_START_ADDR + 512
    magic_value = 0x12345

    auipc_instruction = OP_U_TYPE_AUIPC
    auipc_instruction |= dest_register << 7 # rd = x22
    auipc_instruction |= magic_value << 12 # immediate value

    write_word_to_mem(dut.instruction_ram.mem, start_address, auipc_instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    
    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES + 3)

    result = dut.cpu.reg_file.Registers[dest_register].value.integer
    expected = (magic_value << 12) + start_address
    assert result == expected, f"AUIPC instruction failed: got {result:#010x}, expected {expected:#010x}"