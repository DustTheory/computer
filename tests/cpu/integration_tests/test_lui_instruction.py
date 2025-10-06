import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge
from cocotb.clock import Clock

from cpu.constants import (
    OP_U_TYPE_LUI,

    PIPELINE_CYCLES,
)

wait_ns = 1

@cocotb.test()
async def test_lui_instruction(dut):
    """Test LUI instruction"""

    lui_instruction = OP_U_TYPE_LUI
    lui_instruction |= 1 << 7  # rd = x1
    lui_instruction |= 0x12345 << 12 # immediate value

    dut.cpu.instruction_memory.ram.mem[0].value = lui_instruction

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)
    
    result = dut.cpu.reg_file.Registers[1].value.integer
    expected = 0x12345000
    assert result == expected, f"LUI instruction failed: got {result:#010x}, expected {expected:#010x}"
    