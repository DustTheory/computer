import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_BU,

    PIPELINE_CYCLES,
)

wait_ns = 1

@cocotb.test()
async def test_lbu_instruction(dut):
    """Test lbu instruction (unsigned byte load)"""
    start_address = 80
    rd = 7
    rs1 = 8
    rs1_value = 300
    mem_value = 0xAB
    offset = 12
    mem_address = rs1_value + offset
  
    lbu_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_BU, rs1, offset)
  
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = lbu_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.mem.Memory_Array[mem_address].value = mem_value
  
    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

    expected_value = mem_value  # Should be zero-extended
    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_value, f"LBU instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_value:#010x}"
