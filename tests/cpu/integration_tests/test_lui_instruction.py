import cocotb
from cocotb.triggers import Timer
from constants import (
    OP_U_TYPE_LUI,
)

wait_ns = 10

@cocotb.test()
async def test_lui_instruction(dut):
    """Test LUI instruction"""

    lui_instruction = OP_U_TYPE_LUI
    lui_instruction |= 1 << 7  # rd = x1
    lui_instruction |= 0x12345 << 12 # immediate value
    
    dut.cpu.r_PC.value = 0  # Reset PC to 0
    dut.cpu.instruction_memory.Memory_Array[0].value = lui_instruction
    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    result = dut.cpu.reg_file.Registers[1].value.integer
    expected = 0x12345000
    assert result == expected, f"LUI instruction failed: got {result:#010x}, expected {expected:#010x}"
    