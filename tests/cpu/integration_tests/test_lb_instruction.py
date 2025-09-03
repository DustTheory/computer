import cocotb
from cocotb.triggers import Timer
from cpu.utils import (
    gen_i_type_instruction,
)
from cpu.constants import (
    OP_I_TYPE_LOAD,

    FUNC3_LS_B
)

wait_ns = 1


@cocotb.test()
async def test_lb_instruction_when_equal(dut):
    """Test lb instruction"""

    start_address = 32
    rd = 1
    rs1 = 2
    rs1_value = 10
    mem_value = 12
    offset = 5
    mem_address = rs1_value + offset
    
    lb_instruction = gen_i_type_instruction(OP_I_TYPE_LOAD, rd, FUNC3_LS_B, rs1, offset)

    dut.cpu.r_PC.value = start_address
    dut.cpu.instruction_memory.Memory_Array[start_address>>2].value = lb_instruction
    dut.cpu.reg_file.Registers[rs1].value = rs1_value
    dut.cpu.mem.Memory_Array[mem_address].value = mem_value


    dut.cpu.i_Clock.value = 0
    await Timer(wait_ns, units="ns")
    dut.cpu.i_Clock.value = 1
    await Timer(wait_ns, units="ns")

    assert dut.cpu.reg_file.Registers[rd].value.integer == mem_value, f"LB instruction failed: Rd value is {dut.cpu.reg_file.Registers[rd].value.integer:#010x}, expected {mem_value:#010x}"

