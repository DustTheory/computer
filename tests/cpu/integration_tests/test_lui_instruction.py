import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.constants import (
    OP_U_TYPE_LUI,
    PIPELINE_CYCLES,
    ROM_BOUNDARY_ADDR,
)
from cpu.utils import write_word_to_mem

wait_ns = 1

@cocotb.test()
async def test_lui_instruction(dut):
    """Test LUI instruction"""

    start_address =  ROM_BOUNDARY_ADDR + 0x0
    lui_instruction = OP_U_TYPE_LUI
    lui_instruction |= 1 << 7
    lui_instruction |= 0x12345 << 12

    write_word_to_mem(dut.instruction_ram.mem, start_address, lui_instruction)
    dut.cpu.r_PC.value = start_address

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)
    
    result = dut.cpu.reg_file.Registers[1].value.integer
    expected = 0x12345000
    assert result == expected, f"LUI instruction failed: got {result:#010x}, expected {expected:#010x}"
    