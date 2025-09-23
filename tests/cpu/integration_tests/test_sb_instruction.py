import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_s_type_instruction,
)
from cpu.constants import (
    FUNC3_LS_B
)

wait_ns = 1


@cocotb.test()
async def test_sb_instruction(dut):
    """Test sb instruction"""

    start_address = 0x32
    rs1 = 0x2
    rs2 = 0x3
    rs1_value = 0x10
    rs2_value = 0x20
    imm_value = 0x5
    mem_addres = rs1_value + imm_value
    
    sb_instruction = gen_s_type_instruction(FUNC3_LS_B, rs1, rs2, imm_value)

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = sb_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)

    assert dut.cpu.mem.Memory_Array[mem_addres].value == rs2_value, f"SB instruction failed: Memory at address {mem_addres:#010x} is {dut.cpu.mem.Memory_Array[mem_addres]:#010x}, expected {rs2_value:#010x}"

