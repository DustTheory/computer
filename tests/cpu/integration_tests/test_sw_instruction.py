import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import (
    gen_s_type_instruction,
)
from cpu.constants import (
    FUNC3_LS_W
)

wait_ns = 1

@cocotb.test()
async def test_sw_instruction(dut):
    """Test sw instruction"""
    start_address = 0x48
    rs1 = 0x6
    rs2 = 0x7
    rs1_value = 0x50
    rs2_value = 0xDEADBEEF
    imm_value = 0xA
    mem_address = rs1_value + imm_value

    sw_instruction = gen_s_type_instruction(FUNC3_LS_W, rs1, rs2, imm_value)
    
    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.ram.mem[start_address>>2].value = sw_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, 5)

    assert dut.cpu.mem.Memory_Array[mem_address].value == (rs2_value & 0xFF), f"SW instruction failed: Memory at address {mem_address:#010x} is {dut.cpu.mem.Memory_Array[mem_address].value.integer:#010x}, expected {(rs2_value & 0xFF):#010x}"
    assert dut.cpu.mem.Memory_Array[mem_address + 1].value == ((rs2_value >> 8) & 0xFF), f"SW instruction failed: Memory at address {mem_address+1:#010x} is {dut.cpu.mem.Memory_Array[mem_address+1].value.integer:#010x}, expected {((rs2_value >> 8) & 0xFF):#010x}"
    assert dut.cpu.mem.Memory_Array[mem_address + 2].value == ((rs2_value >> 16) & 0xFF), f"SW instruction failed: Memory at address {mem_address+2:#010x} is {dut.cpu.mem.Memory_Array[mem_address+2].value.integer:#010x}, expected {((rs2_value >> 16) & 0xFF):#010x}"
    assert dut.cpu.mem.Memory_Array[mem_address + 3].value == ((rs2_value >> 24) & 0xFF), f"SW instruction failed: Memory at address {mem_address+3:#010x} is {dut.cpu.mem.Memory_Array[mem_address+3].value.integer:#010x}, expected {((rs2_value >> 24) & 0xFF):#010x}"
