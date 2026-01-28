import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_s_type_instruction,
    send_unhalt_command,
    send_write_pc_command,
    write_word_to_mem,
    uart_send_byte,
    wait_for_pipeline_flush,
)
from cpu.constants import (
    FUNC3_LS_B,
    
    PIPELINE_CYCLES,

    RAM_START_ADDR,
    DEBUG_OP_HALT,
    DEBUG_OP_UNHALT,
)

wait_ns = 1


@cocotb.test()
async def test_sb_instruction(dut):
    """Test sb instruction"""
    start_address =  RAM_START_ADDR + 0x40
    rs1 = 0x4
    rs2 = 0x5
    rs1_value = 0
    rs2_value = 0x20
    imm_value = 0
    mem_address = rs1_value + imm_value
    word_index = mem_address

    sh_instruction = gen_s_type_instruction(FUNC3_LS_B, rs1, rs2, imm_value)

    write_word_to_mem(dut.instruction_ram.mem, start_address, sh_instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)


    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    expected = rs2_value & 0xFF
    assert dut.data_ram.mem[word_index].value == expected, f"SB instruction failed: Memory byte {word_index} is {dut.data_ram.mem[word_index].value.integer:#04x}, expected {expected:#04x}"
