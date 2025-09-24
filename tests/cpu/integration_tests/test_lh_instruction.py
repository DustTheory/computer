import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_H
)

wait_ns = 1


@cocotb.test()
async def test_lh_instruction_when_equal(dut):
    """Test lh instruction"""

    start_address = 0
    rd = 10
    rs1 = 11
    rs1_value = 100
    mem_value = 0x1234
    offset = 20
    mem_address = rs1_value + offset
    
    lb_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_H, rs1, offset)

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = lb_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.mem.Memory_Array[mem_address].value = mem_value & 0xFF
    dut.cpu.mem.Memory_Array[mem_address + 1].value = mem_value >> 8

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)

    assert dut.cpu.reg_file.Registers[rd].value.integer == mem_value, f"LH instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {mem_value:#010x}"

