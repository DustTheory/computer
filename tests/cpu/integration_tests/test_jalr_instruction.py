import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_JALR,

    IMM_I_TYPE
)

wait_ns = 1


@cocotb.test()
async def test_jalr_instruction(dut):
    """Test JALR instruction"""

    start_address = 256
    dest_register = 1
    rs1 = 2
    rs1_value = 0x200
    imm_value = 0b010101010101
    jalr_instruction = gen_i_type_instruction(OP_I_TYPE_JALR, dest_register, 0, rs1, imm_value)
    i_type_imm = 0b00000000000000000000010101010101
    expected_pc = rs1_value + i_type_imm
    expected_register_value = start_address + 4

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = jalr_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value


    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)

    assert dut.cpu.r_PC.value.integer == expected_pc, f"JALR instruction failed: PC is {dut.cpu.r_PC.value.integer:#010x}, expected {expected_pc:#010x}"
    assert dut.cpu.reg_file.Registers[dest_register].value.integer == expected_register_value, f"JALR instruction failed: Register x{dest_register} is {dut.cpu.reg_file.Registers[dest_register].value.integer:#010x}, expected {expected_register_value:#010x}"