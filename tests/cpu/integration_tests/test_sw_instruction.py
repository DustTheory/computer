import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge
from cocotb.clock import Clock

from cpu.utils import (
    gen_s_type_instruction,
    write_word_to_mem,
)
from cpu.constants import (
    FUNC3_LS_W,

    PIPELINE_CYCLES,

    ROM_BOUNDARY_ADDR,
)

wait_ns = 1

@cocotb.test()
async def test_sw_instruction(dut):
    """Test sw instruction"""
    start_address =  ROM_BOUNDARY_ADDR + 0
    rs1 = 0x6
    rs2 = 0x7
    rs1_value = 0
    rs2_value = 0xDEADBEEF
    imm_value = 0
    mem_address = rs1_value + imm_value

    sw_instruction = gen_s_type_instruction(FUNC3_LS_W, rs1, rs2, imm_value)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    dut.cpu.r_PC.value = start_address
    write_word_to_mem(dut.instruction_ram.mem, start_address, sw_instruction)
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.reg_file.Registers[rs2].value = rs2_value


    await ClockCycles(dut.i_Clock, PIPELINE_CYCLES)

    for i in range(4):
        expected_byte = (rs2_value >> (8*i)) & 0xFF
        assert dut.data_ram.mem[mem_address + i].value == expected_byte, (
            f"SW instruction failed: byte {mem_address+i} is {dut.data_ram.mem[mem_address+i].value.integer:#04x}, expected {expected_byte:#04x}")