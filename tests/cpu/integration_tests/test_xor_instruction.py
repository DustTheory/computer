import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_r_type_instruction
from cpu.constants import FUNC3_ALU_XOR, PIPELINE_CYCLES

wait_ns = 1

@cocotb.test()
async def test_xor_instruction(dut):
    """Test xor instruction"""
    tests = [
        (0x1, 0x2, 0x3),
        (0xF0F0F0F0, 0x0F0F0F0F, 0xFFFFFFFF),
        (0xFFFFFFFF, 0xFFFFFFFF, 0x0),
        (0x12345678, 0x87654321, 0x95511559),
        (0, 0, 0),
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    for rs1_value, rs2_value, expected_result in tests:
        instruction = gen_r_type_instruction(rd, FUNC3_ALU_XOR, rs1, rs2, 0)
        
        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.ram.mem[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.reg_file.Registers[rs2].value = rs2_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)

    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"XOR instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
