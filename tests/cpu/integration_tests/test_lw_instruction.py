import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    write_word_to_mem,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_W,

    PIPELINE_CYCLES,
)

wait_ns = 1

@cocotb.test()
async def test_lw_instruction(dut):
    """Test lw instruction"""
    start_address = 64
    rd = 5
    rs1 = 6
    rs1_value = 0
    mem_value = 0xDEADBEEF
    offset = 0
    mem_address = rs1_value + offset

    lw_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_W, rs1, offset)
  
    dut.cpu.r_PC.value = start_address
    write_word_to_mem(dut.cpu.instruction_memory.ram.mem, start_address, lw_instruction)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value

    write_word_to_mem(dut.cpu.mem.ram.mem, mem_address, mem_value)
    
    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

    assert dut.cpu.reg_file.Registers[rd].value.integer == mem_value, f"LW instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {mem_value:#010x}"
