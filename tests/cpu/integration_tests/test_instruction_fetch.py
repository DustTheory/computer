import cocotb
from cocotb.triggers import Timer

wait_ns = 1

@cocotb.test()
async def test_single_instruction_fetch(dut):
    """Test instruction fetch from instruction memory"""
    dut._log.info("Starting instruction fetch test")

    # Load a known instruction into instruction memory
    test_instruction = 0x12345678
    dut.cpu.instruction_memory.Memory_Array[0].value = test_instruction

    # Set PC to 0 to fetch the first instruction
    dut.cpu.r_PC.value = 0
    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    
    # Rising edge of the clock to fetch instruction
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")

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

    # Load a known instruction into instruction memory
    dut.cpu.instruction_memory.Memory_Array[0].value = instructions[0]
    dut.cpu.instruction_memory.Memory_Array[1].value = instructions[1]
    dut.cpu.instruction_memory.Memory_Array[2].value = instructions[2]

    dut.cpu.r_PC.value = 0

    for i in range(3):
        dut.cpu.i_Clock.value = 0
        await Timer(wait_ns, units="ns")

        # Rising edge of the clock to fetch instruction
        dut.cpu.i_Clock.value = 1
        await Timer(wait_ns, units="ns")

        fetched_instruction = dut.cpu.w_Instruction.value.integer
        expected = instructions[i]
        assert fetched_instruction == expected, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {expected:#010x}"
