import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

from cpu.constants import (
    OP_J_TYPE,
    RAM_START_ADDR,
)
from cpu.utils import send_unhalt_command, send_write_pc_command, write_word_to_mem, wait_for_pipeline_flush

wait_ns = 1

@cocotb.test()
async def test_jal_instruction(dut):
    """Test JAL instruction"""

    dest_register = 13
    start_address =  RAM_START_ADDR + 256
    magic_value = 0b00000000000000000000001010101010000000000
    
    j_type_imm = 0b10101010100

    expected_pc = start_address + j_type_imm
    expected_register_value = start_address + 4

    jal_instruction = OP_J_TYPE
    jal_instruction |= dest_register << 7 
    jal_instruction |= magic_value << 12

    write_word_to_mem(dut.instruction_ram.mem, start_address, jal_instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
    await send_unhalt_command(dut)

    max_cycles = 200
    pc_reached = False
    reg_reached = False
    for _ in range(max_cycles):
        await RisingEdge(dut.i_Clock)
        if dut.cpu.r_PC.value.integer == expected_pc:
            pc_reached = True
        if dut.cpu.reg_file.Registers[dest_register].value.integer == expected_register_value:
            reg_reached = True
        if pc_reached and reg_reached:
            break

    assert pc_reached, "JAL target PC not reached"
    assert reg_reached, f"JAL link register x{dest_register} incorrect: {dut.cpu.reg_file.Registers[dest_register].value.integer:#010x} expected {expected_register_value:#010x}"