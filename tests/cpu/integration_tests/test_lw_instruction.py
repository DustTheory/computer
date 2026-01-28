import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    send_write_pc_command,
    send_unhalt_command,
    wait_for_pipeline_flush,
    write_word_to_mem,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_W,

    PIPELINE_CYCLES,

    RAM_START_ADDR,
)

wait_ns = 1

@cocotb.test()
async def test_lw_instruction(dut):
    """Test lw instruction"""
    start_address =  RAM_START_ADDR + 64
    rd = 5
    rs1 = 6
    rs1_value = 0
    mem_value = 0xDEADBEEF
    offset = 0
    mem_address = rs1_value + offset

    lw_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_W, rs1, offset)
  
    write_word_to_mem(dut.instruction_ram.mem, start_address, lw_instruction)
    write_word_to_mem(dut.data_ram.mem, mem_address, mem_value)
    
    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    assert dut.cpu.reg_file.Registers[rd].value.integer == mem_value, f"LW instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {mem_value:#010x}"
