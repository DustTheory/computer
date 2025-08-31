import cocotb
from cocotb.triggers import Timer

wait_ns = 1

@cocotb.test()
async def test_read_instruction(dut):
    """Test reading instruction memory"""

    instructions = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321]

    dut.instruction_memory.Memory_Array[0].value = instructions[0]
    dut.instruction_memory.Memory_Array[1].value = instructions[1]
    dut.instruction_memory.Memory_Array[2].value = instructions[2]
    dut.instruction_memory.Memory_Array[3].value = instructions[3]

    for i in range(4):
        dut.instruction_memory.i_Instruction_Addr.value = i*4
        dut.instruction_memory.i_Clock.value = 1
        await Timer(wait_ns, units="ns")
        dut.instruction_memory.i_Clock.value = 0
        await Timer(wait_ns, units="ns")
        value = dut.instruction_memory.o_Instruction.value.integer
        expected = instructions[i]
        assert value == expected, f"Read instruction failed at address {i}: got {value:#010x}, expected {expected:#010x}"