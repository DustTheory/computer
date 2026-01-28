import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

from cpu.utils import (
    gen_b_type_instruction,
    send_unhalt_command,
    send_write_pc_command,
    write_word_to_mem,
    wait_for_pipeline_flush,
)
from cpu.constants import (
    FUNC3_BRANCH_BEQ,
    RAM_START_ADDR,
)

wait_ns = 1


@cocotb.test()
async def test_beq_instruction_when_equal(dut):
    """Test BEQ instruction"""

    start_address =  RAM_START_ADDR + 16
    rs1 = 2
    rs1_value = 0x200
    rs2 = 3
    rs2_value = 0x200
    offset = 1024

    
    beq_instruction = gen_b_type_instruction(FUNC3_BRANCH_BEQ, rs1, rs2, offset)
    expected_pc = start_address + offset

    write_word_to_mem(dut.instruction_ram.mem, start_address, beq_instruction)

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

    max_cycles = 100
    for _ in range(max_cycles):
        await RisingEdge(dut.i_Clock)
        if dut.cpu.r_PC.value.integer == expected_pc:
            break
    else:
        raise AssertionError("Timeout waiting for BEQ taken to reach target PC")

    assert dut.cpu.r_PC.value.integer == expected_pc, f"BEQ instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"

@cocotb.test()
async def test_beq_instruction_when_not_equal(dut):
    """Test BEQ instruction"""

    start_address =  RAM_START_ADDR + 16
    rs1 = 2
    rs1_value = 0x200
    rs2 = 3
    rs2_value = 0x201
    offset = 1024

    beq_instruction = gen_b_type_instruction(FUNC3_BRANCH_BEQ, rs1, rs2, offset)
    expected_pc = start_address + 4

    write_word_to_mem(dut.instruction_ram.mem, start_address, beq_instruction)

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

    # UNHALT CPU to start execution
    await send_unhalt_command(dut)

    max_cycles = 100
    for _ in range(max_cycles):
        await RisingEdge(dut.i_Clock)
        if dut.cpu.r_PC.value.integer == expected_pc:
            break
    else:
        raise AssertionError("Timeout waiting for BEQ not-taken to advance PC by 4")

    assert dut.cpu.r_PC.value.integer == expected_pc, f"BEQ instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"