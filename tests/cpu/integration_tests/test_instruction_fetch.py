import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock

from cpu.utils import write_word_to_mem, write_instructions

wait_ns = 1

@cocotb.test()
async def test_single_instruction_fetch(dut):
    """Test instruction fetch from instruction memory"""
    dut._log.info("Starting instruction fetch test")

    test_instruction = 0x12345678
    write_word_to_mem(dut.instruction_ram.mem, 0, test_instruction)
    write_word_to_mem(dut.instruction_ram.mem, 4, 0x9ABCDEF0)
    write_word_to_mem(dut.instruction_ram.mem, 8, 0x0FEDCBA9)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0

    await RisingEdge(dut.cpu.w_Instruction_Valid)

    fetched_instruction = dut.cpu.w_Instruction.value.integer
    assert fetched_instruction == test_instruction, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {test_instruction:#010x}"


@cocotb.test()
async def test_multiple_instruction_fetch(dut):
    """Test fetching multiple instructions from instruction_memory"""
    dut._log.info("Starting multiple instruction fetch test")

    instructions = [
        0x12345678,
        0xABADBABE,
        0xB16B00B5,
    ]

    write_instructions(dut.instruction_ram.mem, 0, instructions)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(1):
        await RisingEdge(dut.cpu.w_Instruction_Valid)
        dut._log.info(f"Fetched instruction {i}: {dut.cpu.w_Instruction.value.integer:#010x}")
        dut._log.info(f"Instruction Valid: {dut.cpu.w_Instruction_Valid.value}")

        fetched_instruction = dut.cpu.w_Instruction.value.integer
        expected = instructions[i]
        assert fetched_instruction == expected, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {expected:#010x}"
