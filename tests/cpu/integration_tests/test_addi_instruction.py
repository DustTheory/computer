import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_i_type_instruction, write_word_to_mem
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_ADD_SUB, PIPELINE_CYCLES, ROM_BOUNDARY_ADDR

wait_ns = 1

@cocotb.test()
async def test_addi_instruction(dut):
    """Test addi instruction"""

    start_address = ROM_BOUNDARY_ADDR + 0x0
    rs1 = 1
    rs1_value = 0x20
    rd = 3
    imm_value = 0x10
    expected_result = rs1_value + imm_value

    instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_ADD_SUB, rs1, imm_value)

    write_word_to_mem(dut.instruction_ram.mem, start_address, instruction)
    dut.cpu.r_PC.value = start_address
    dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"ADD instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
