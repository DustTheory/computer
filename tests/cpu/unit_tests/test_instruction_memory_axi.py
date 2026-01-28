import cocotb
from cocotb.triggers import Timer

from cpu.utils import write_instructions, write_instructions_rom
from cpu.constants import RAM_START_ADDR, CPU_BASE_ADDR

wait_ns = 1

@cocotb.test()
async def test_read_instruction(dut):
    """Test reading instruction memory"""

    instructions = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321]

    write_instructions(dut.instruction_ram.mem, RAM_START_ADDR, instructions)

    for instruction_index in range(4):
        dut.instruction_memory_axi.i_Instruction_Addr.value = RAM_START_ADDR + instruction_index*4

        for clock_cnt in range(10):
            dut.i_Clock.value = 1
            await Timer(wait_ns, units="ns")
            dut.i_Clock.value = 0
            await Timer(wait_ns, units="ns")
            dut._log.info(f"Cycle {clock_cnt}")
            dut._log.info(f"  State: {dut.instruction_memory_axi.r_State.value}")
            dut._log.info(f"  ARREADY: {dut.instruction_memory_axi.s_axil_arready.value}")
            dut._log.info(f"  RVALID: {dut.instruction_memory_axi.s_axil_rvalid.value}")
            dut._log.info(f"  RDATA: {dut.instruction_memory_axi.s_axil_rdata.value}")
            dut.log.info(f"  Instruction Valid: {dut.instruction_memory_axi.o_Instruction_Valid.value}")
            dut.log.info(f"  Instruction: {dut.instruction_memory_axi.o_Instruction.value}")
            if dut.instruction_memory_axi.o_Instruction_Valid.value:
                break

        value = dut.instruction_memory_axi.o_Instruction.value.integer
        expected = instructions[instruction_index]
        assert value == expected, f"Read instruction failed at address {instruction_index*4:#06x}: got {value:#010x}, expected {expected:#010x}"


@cocotb.test()
async def test_read_instruction_rom(dut):
    """Test reading instruction memory"""

    instructions = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321]

    write_instructions_rom(dut.instruction_memory_axi.rom, CPU_BASE_ADDR, instructions)

    for instruction_index in range(4):
        dut.instruction_memory_axi.i_Instruction_Addr.value = CPU_BASE_ADDR + instruction_index*4

        for clock_cnt in range(10):
            dut.i_Clock.value = 1
            await Timer(wait_ns, units="ns")
            dut.i_Clock.value = 0
            await Timer(wait_ns, units="ns")
            dut._log.info(f"Cycle {clock_cnt}")
            dut._log.info(f"  State: {dut.instruction_memory_axi.r_State.value}")
            dut._log.info(f"  ARREADY: {dut.instruction_memory_axi.s_axil_arready.value}")
            dut._log.info(f"  RVALID: {dut.instruction_memory_axi.s_axil_rvalid.value}")
            dut._log.info(f"  RDATA: {dut.instruction_memory_axi.s_axil_rdata.value}")
            dut.log.info(f"  Instruction Valid: {dut.instruction_memory_axi.o_Instruction_Valid.value}")
            dut.log.info(f"  Instruction: {dut.instruction_memory_axi.o_Instruction.value}")
            if dut.instruction_memory_axi.o_Instruction_Valid.value:
                break

        value = dut.instruction_memory_axi.o_Instruction.value.integer
        expected = instructions[instruction_index]
        assert value == expected, f"Read instruction failed at address {instruction_index*4:#06x}: got {value:#010x}, expected {expected:#010x}"
