import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    write_word_to_mem,
    write_byte_to_mem,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,
    FUNC3_LS_BU,
    PIPELINE_CYCLES,
    ROM_BOUNDARY_ADDR,
)

wait_ns = 1

@cocotb.test()
async def test_lbu_instruction(dut):
    """Test lbu instruction (unsigned byte load)"""

    rd = 5
    rs1 = 2
    start_address =  ROM_BOUNDARY_ADDR + 0
    rs1_value = 0
    offset = 0
    mem_value = 0xAB
    mem_address = rs1_value + offset

    write_byte_to_mem(dut.data_ram.mem, mem_address, mem_value & 0xFF)

    lbu_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_BU, rs1, offset)

    dut.cpu.r_PC.value = start_address
    write_word_to_mem(dut.instruction_ram.mem, start_address, lbu_instruction)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    result = dut.cpu.reg_file.Registers[rd].value.integer
    assert result == mem_value, f"LBU instruction failed: Rd value is {result:#010x}, expected {mem_value:#010x}"
