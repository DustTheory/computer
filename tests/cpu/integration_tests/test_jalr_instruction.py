import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_JALR,
)
from cpu.utils import write_word_to_mem

wait_ns = 1


@cocotb.test()
async def test_jalr_instruction(dut):
    """Test JALR instruction"""

    start_address = 256
    dest_register = 1
    rs1 = 2
    rs1_value = 0x200
    imm_value = 0b010101010101
    jalr_instruction = gen_i_type_instruction(OP_I_TYPE_JALR, dest_register, 0, rs1, imm_value)
    i_type_imm = 0b00000000000000000000010101010101
    expected_pc = rs1_value + i_type_imm
    expected_register_value = start_address + 4

    write_word_to_mem(dut.instruction_ram.mem, start_address, jalr_instruction)
    dut.cpu.r_PC.value = start_address
    dut.cpu.reg_file.Registers[rs1].value = rs1_value


    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    max_cycles = 200
    pc_reached = False
    reg_reached = False
    for _ in range(max_cycles):
        await RisingEdge(dut.i_Clock)
        if not pc_reached and dut.cpu.r_PC.value.integer == expected_pc:
            pc_reached = True
        if dut.cpu.reg_file.Registers[dest_register].value.integer == expected_register_value:
            reg_reached = True
        if pc_reached and reg_reached:
            break
    else:
        raise AssertionError("Timeout waiting for JALR PC/Link register commit")

    assert pc_reached, "JALR target PC not reached"
    assert reg_reached, f"JALR link register x{dest_register} incorrect: {dut.cpu.reg_file.Registers[dest_register].value.integer:#010x} expected {expected_register_value:#010x}"