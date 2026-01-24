import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

from cpu.utils import (
    gen_b_type_instruction,
    gen_i_type_instruction,
    write_word_to_mem,
)
from cpu.constants import (
    FUNC3_BRANCH_BNE,
    FUNC3_ALU_ADD_SUB,
    OP_I_TYPE_ALU,
    ROM_BOUNDARY_ADDR
)

wait_ns = 1

@cocotb.test()
async def test_bne_instruction_when_not_equal(dut):
    """Test BNE instruction: rs1 != rs2 - with pipeline flush verification"""
    start_address = ROM_BOUNDARY_ADDR + 16
    rs1 = 2
    rs1_value = 0x200
    rs2 = 3
    rs2_value = 0x201
    rd_poison = 4
    offset = 1024

    bne_instruction = gen_b_type_instruction(FUNC3_BRANCH_BNE, rs1, rs2, offset)
    poison_instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd_poison, FUNC3_ALU_ADD_SUB, 0, 0x42)
    expected_pc = start_address + offset

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Write instructions to memory before setting PC
    write_word_to_mem(dut.instruction_ram.mem, start_address, bne_instruction)
    write_word_to_mem(dut.instruction_ram.mem, start_address + 4, poison_instruction)
    await ClockCycles(dut.i_Clock, 3)

    dut.cpu.r_PC.value = start_address
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value
    dut.cpu.reg_file.Registers[rd_poison].value = 0

    # Track pipeline flush signals
    flush_pipeline_seen = False
    flushing_pipeline_seen = False

    max_cycles = 100
    for _ in range(max_cycles):
        await RisingEdge(dut.i_Clock)

        # Monitor pipeline flush signals
        if dut.cpu.cu.o_Flush_Pipeline.value == 1:
            flush_pipeline_seen = True
        if dut.cpu.r_Flushing_Pipeline.value == 1:
            flushing_pipeline_seen = True

        if dut.cpu.r_PC.value.integer == expected_pc:
            break
    else:
        current_pc = dut.cpu.r_PC.value.integer
        raise AssertionError(f"Timeout waiting for BNE taken to reach target PC. Current PC: {current_pc:#x}, Expected: {expected_pc:#x}")

    assert dut.cpu.r_PC.value.integer == expected_pc, f"BNE instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"
    assert flush_pipeline_seen, "Pipeline flush signal (o_Flush_Pipeline) was not asserted during branch"
    assert flushing_pipeline_seen, "Pipeline flushing state (r_Flushing_Pipeline) was not asserted"

    # Verify the poison instruction did NOT execute
    poison_reg_value = dut.cpu.reg_file.Registers[rd_poison].value.integer
    assert poison_reg_value == 0, f"Wrong-path instruction executed! Poison register {rd_poison} = {poison_reg_value:#x}, expected 0. Pipeline flush failed!"

@cocotb.test()
async def test_bne_instruction_when_equal(dut):
    """Test BNE instruction: rs1 == rs2 - branch not taken, verify no flush"""
    start_address = ROM_BOUNDARY_ADDR + 16
    rs1 = 2
    rs1_value = 0x200
    rs2 = 3
    rs2_value = 0x200
    rd_next = 4
    offset = 1024

    bne_instruction = gen_b_type_instruction(FUNC3_BRANCH_BNE, rs1, rs2, offset)
    next_instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd_next, FUNC3_ALU_ADD_SUB, 0, 0x55)
    expected_pc = start_address + 4

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    dut.cpu.r_PC.value = start_address
    write_word_to_mem(dut.instruction_ram.mem, start_address, bne_instruction)
    write_word_to_mem(dut.instruction_ram.mem, start_address + 4, next_instruction)

    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value
    dut.cpu.reg_file.Registers[rd_next].value = 0

    # Track pipeline flush signals
    flush_pipeline_seen = False
    flushing_pipeline_seen = False

    max_cycles = 100
    for _ in range(max_cycles):
        await RisingEdge(dut.i_Clock)

        # Monitor pipeline flush signals
        if dut.cpu.cu.o_Flush_Pipeline.value == 1:
            flush_pipeline_seen = True
        if dut.cpu.r_Flushing_Pipeline.value == 1:
            flushing_pipeline_seen = True

        if dut.cpu.r_PC.value.integer == expected_pc:
            break
    else:
        raise AssertionError("Timeout waiting for BNE not-taken to advance PC by 4")

    await ClockCycles(dut.i_Clock, 10)

    assert dut.cpu.r_PC.value.integer >= expected_pc, f"BNE instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected >= {expected_pc:#010x}"
    assert not flush_pipeline_seen, "Pipeline flush signal incorrectly asserted for not-taken branch"
    assert not flushing_pipeline_seen, "Pipeline flushing state incorrectly asserted for not-taken branch"

    # Verify the next instruction executed
    next_reg_value = dut.cpu.reg_file.Registers[rd_next].value.integer
    assert next_reg_value == 0x55, f"Next instruction did not execute! Register {rd_next} = {next_reg_value:#x}, expected 0x55"
