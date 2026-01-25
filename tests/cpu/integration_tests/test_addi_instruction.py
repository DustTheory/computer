import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_i_type_instruction, send_unhalt_command, send_write_pc_command, write_word_to_mem, uart_send_byte, wait_for_pipeline_flush
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_ADD_SUB, PIPELINE_CYCLES, RAM_START_ADDR, DEBUG_OP_HALT, DEBUG_OP_UNHALT

wait_ns = 1

@cocotb.test()
async def test_addi_instruction(dut):
    """Test addi instruction"""

    start_address = RAM_START_ADDR + 0x0
    rs1 = 1
    rs1_value = 0x20
    rd = 3
    imm_value = 0x10
    expected_result = rs1_value + imm_value

    instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_ADD_SUB, rs1, imm_value)
    write_word_to_mem(dut.instruction_ram.mem, start_address, instruction)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await send_write_pc_command(dut, start_address)
    await wait_for_pipeline_flush(dut)
   
    dut.cpu.reg_file.Registers[rs1].value = rs1_value & 0xFFFFFFFF
    await send_unhalt_command(dut)

    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES + 3)

    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"ADD instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
