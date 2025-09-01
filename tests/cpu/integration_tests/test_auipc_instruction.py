import cocotb
from cocotb.triggers import Timer
from cpu.constants import (
    OP_U_TYPE_AUIPC,
)

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

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = auipc_instruction

    dut.cpu.i_Reset.value = 0
    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")

    result = dut.cpu.reg_file.Registers[dest_register].value.integer
    expected = (magic_value << 12) + start_address
    assert result == expected, f"AUIPC instruction failed: got {result:#010x}, expected {expected:#010x}"