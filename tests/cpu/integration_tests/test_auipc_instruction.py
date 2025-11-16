import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.constants import (
    OP_U_TYPE_AUIPC,

    PIPELINE_CYCLES,
)
from cpu.utils import write_word_to_mem

wait_ns = 1

@cocotb.test()
async def test_auipc_instruction(dut):
    """Test AUIPC instruction"""

    dest_register = 22
    start_address = 512
    magic_value = 0x12345

    auipc_instruction = OP_U_TYPE_AUIPC
    auipc_instruction |= dest_register << 7 # rd = x22
    auipc_instruction |= magic_value << 12 # immediate value

    write_word_to_mem(dut.instruction_ram.mem, start_address, auipc_instruction)
    dut.cpu.r_PC.value = start_address

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    result = dut.cpu.reg_file.Registers[dest_register].value.integer
    expected = (magic_value << 12) + start_address
    assert result == expected, f"AUIPC instruction failed: got {result:#010x}, expected {expected:#010x}"