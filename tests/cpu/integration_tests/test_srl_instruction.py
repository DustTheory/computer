import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock

from cpu.utils import gen_r_type_instruction
from cpu.constants import FUNC3_ALU_SRL_SRA

wait_ns = 1

@cocotb.test()
async def test_srl_instruction(dut):
    """Test srl instruction"""
    tests = [
        (0x8, 1, 0x4),
        (0xF0, 4, 0xF),
        (0x80000000, 1, 0x40000000),
        (0xFFFFFFFF, 1, 0x7FFFFFFF),
        (0x1, 1, 0x0),
        (0x80000000, 31, 0x1),
    ]

    start_address = 0x0
    rs1 = 1
    rs2 = 2
    rd = 3

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    for rs1_value, rs2_value, expected_result in tests:
        instruction = gen_r_type_instruction(rd, FUNC3_ALU_SRL_SRA, rs1, rs2, 0)

        dut.cpu.r_PC.value = start_address
        dut.cpu.instruction_memory.ram.mem[start_address>>2].value = instruction
        dut.cpu.reg_file.Registers[rs1].value = rs1_value
        dut.cpu.reg_file.Registers[rs2].value = rs2_value

        dut.cpu.i_Reset.value = 1
        await ClockCycles(dut.cpu.i_Clock, 1)
        dut.cpu.i_Reset.value = 0
        await ClockCycles(dut.cpu.i_Clock, 1)

        await ClockCycles(dut.cpu.i_Clock, 5)
                
        assert dut.cpu.reg_file.Registers[rd].value.integer == expected_result, f"SRL instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {expected_result:#010x}"
