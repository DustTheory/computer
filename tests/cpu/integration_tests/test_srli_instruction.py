import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_i_type_instruction
from cpu.constants import OP_I_TYPE_ALU, FUNC3_ALU_SRL_SRA, PIPELINE_CYCLES

wait_ns = 1

@cocotb.test()
async def test_srli_instruction(dut):
    """Test srli instruction"""

    tests = [
        # imm value is sign-extended, 12 bytes
        # (rs1_value, imm_value, expected_result)
        (0xFF, 4, 0xF),
        (0xAA, 2, 0x2A),
        (0xFFFFFFFF, 31, 0x1),
        (0xFFFFFFFF, 1, 0X7FFFFFFF),
    ]

    start_address = 0x0
    rs1 = 1
    rd = 3

    for rs1_value, imm_value, expected_result in tests:
        instruction = gen_i_type_instruction(OP_I_TYPE_ALU, rd, FUNC3_ALU_SRL_SRA, rs1, imm_value)

        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.ram.mem[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    await ClockCycles(dut.cpu.i_Clock, PIPELINE_CYCLES)
        
    assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"SRLI instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
