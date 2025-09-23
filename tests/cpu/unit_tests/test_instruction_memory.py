import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

wait_ns = 1

@cocotb.test()
async def test_read_instruction(dut):
    """Test reading instruction memory"""

    instructions = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321]

    dut.instruction_memory.ram.mem[0].value = instructions[0]
    dut.instruction_memory.ram.mem[1].value = instructions[1]
    dut.instruction_memory.ram.mem[2].value = instructions[2]
    dut.instruction_memory.ram.mem[3].value = instructions[3]

    clock = Clock(dut.instruction_memory.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.instruction_memory.i_Reset.value = 1
    await ClockCycles(dut.instruction_memory.i_Clock, 1)
    dut.instruction_memory.i_Reset.value = 0
    await ClockCycles(dut.instruction_memory.i_Clock, 1)

    for i in range(4):
        dut.instruction_memory.i_Instruction_Addr.value = i*4

        await RisingEdge(dut.instruction_memory.o_Instruction_Valid)

        value = dut.instruction_memory.o_Instruction.value.integer
        expected = instructions[i]
        assert value == expected, f"Read instruction failed at address {i}: got {value:#010x}, expected {expected:#010x}"