import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    write_word_to_mem,
    write_half_to_mem,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,
    FUNC3_LS_H,
    PIPELINE_CYCLES,
)

wait_ns = 1


@cocotb.test()
async def test_lh_instruction_when_equal(dut):
    """Test lh instruction"""

    rd = 5
    rs1 = 2
    start_address = 0
    mem_value = 0xBEEF

    write_half_to_mem(dut.data_ram.mem, start_address, mem_value & 0xFFFF)

    offset = 0
    lh_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_H, rs1, offset)

    dut.cpu.r_PC.value = 0
    dut.cpu.reg_file.Registers[rs1].value = start_address
    write_word_to_mem(dut.instruction_ram.mem, 0, lh_instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    result = dut.cpu.reg_file.Registers[rd].value.integer & 0xFFFF
    assert result == (mem_value & 0xFFFF), f"LH instruction failed: Rd value is {result:#010x}, expected {(mem_value & 0xFFFF):#010x}"

