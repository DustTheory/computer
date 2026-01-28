import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
    send_unhalt_command,
    send_write_pc_command,
    write_byte_to_mem,
    write_word_to_mem,
    wait_for_pipeline_flush,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_B,

    PIPELINE_CYCLES,

    RAM_START_ADDR,
)

wait_ns = 1


@cocotb.test()
async def test_lb_instruction_when_equal(dut):
    """Test lb instruction"""

    start_address =  RAM_START_ADDR + 0
    rd = 1
    rs1 = 2
    rs1_value = 0
    mem_value = 12
    offset = 0
    mem_address = rs1_value + offset

    lb_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_B, rs1, offset)

    write_word_to_mem(dut.instruction_ram.mem, start_address, lb_instruction)
    write_byte_to_mem(dut.data_ram.mem, mem_address, mem_value & 0xFF)

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

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES + 3)

    assert dut.cpu.reg_file.Registers[rd].value.integer == mem_value, f"LB instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {mem_value:#010x}"

