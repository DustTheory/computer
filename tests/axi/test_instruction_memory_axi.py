import cocotb
from cocotb.triggers import Timer

wait_ns = 1

@cocotb.test()
async def test_read_instruction(dut):
    """Test reading instruction memory"""

    instructions = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321]

    dut.instruction_memory_axi.ram.mem[0].value = instructions[0]
    dut.instruction_memory_axi.ram.mem[1].value = instructions[1]
    dut.instruction_memory_axi.ram.mem[2].value = instructions[2]
    dut.instruction_memory_axi.ram.mem[3].value = instructions[3]

    for instruction_index in range(4):

        dut.instruction_memory_axi.i_Instruction_Addr.value = instruction_index*4

        for clock_cnt in range(10):
            dut.instruction_memory_axi.i_Clock.value = 1
            await Timer(wait_ns, units="ns")
            dut.instruction_memory_axi.i_Clock.value = 0
            await Timer(wait_ns, units="ns")
            dut._log.info(f"Cycle {clock_cnt}")
            dut._log.info(f"  State: {dut.instruction_memory_axi.r_State.value}")
            dut._log.info(f"  ARREADY: {dut.instruction_memory_axi.w_axil_arready.value}")
            dut._log.info(f"  RVALID: {dut.instruction_memory_axi.w_axil_rvalid.value}")
            dut._log.info(f"  RDATA: {dut.instruction_memory_axi.w_axil_rdata.value}")
            dut.log.info(f"  Instruction Valid: {dut.instruction_memory_axi.o_Instruction_Valid.value}")
            dut.log.info(f"  Instruction: {dut.instruction_memory_axi.o_Instruction.value}")
            if dut.instruction_memory_axi.o_Instruction_Valid.value:
                break


        value = dut.instruction_memory_axi.o_Instruction.value.integer
        expected = instructions[instruction_index]
        assert value == expected, f"Read instruction failed at address 0: got {value:#010x}, expected {expected:#010x}"
