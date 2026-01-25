import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    send_unhalt_command,
    send_write_pc_command,
    write_word_to_mem,
    write_half_to_mem,
    wait_for_pipeline_flush,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_HU,

    PIPELINE_CYCLES,
    
    RAM_START_ADDR,
)

wait_ns = 1

@cocotb.test()
async def test_lhu_instruction(dut):
    """Test lhu instruction (unsigned halfword load)"""
    start_address =  RAM_START_ADDR + 96
    rd = 9
    rs1 = 10
    rs1_value = 400
    mem_value = 0xBEEF
    offset = 16
    mem_address = rs1_value + offset
    
    lhu_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_HU, rs1, offset)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    write_word_to_mem(dut.instruction_ram.mem, start_address, lhu_instruction)
    write_half_to_mem(dut.data_ram.mem, mem_address, mem_value & 0xFFFF)

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    expected_value = mem_value  # Should be zero-extended
    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_value, f"LHU instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_value:#010x}"
