import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, Timer
from cocotb.clock import Clock

from cpu.constants import (
    OP_U_TYPE_LUI,
)

wait_ns = 1

@cocotb.test()
async def test_lui_instruction(dut):
    """Test LUI instruction"""

    lui_instruction = OP_U_TYPE_LUI
    lui_instruction |= 1 << 7  # rd = x1
    lui_instruction |= 0x12345 << 12 # immediate value

    dut.cpu.instruction_memory.ram.mem[0].value = lui_instruction

    clock = Clock(dut.cpu.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.cpu.i_Reset.value = 1
    await ClockCycles(dut.cpu.i_Clock, 1)
    dut.cpu.i_Reset.value = 0
    await ClockCycles(dut.cpu.i_Clock, 1)

    # await RisingEdge(dut.cpu.mem.o_Data_Valid)
    # await ClockCycles(dut.cpu.i_Clock, 5)

    for clock_cnt in range(10):
        await ClockCycles(dut.cpu.i_Clock, 1)

        dut._log.info(f"Cycle {clock_cnt}")
        dut._log.info(f"  State: {dut.cpu.mem.r_State.value}")
        dut._log.info(f"  ARREADY: {dut.cpu.mem.w_axil_arready.value}")
        dut._log.info(f"  RVALID: {dut.cpu.mem.w_axil_rvalid.value}")
        dut._log.info(f"  RDATA: {dut.cpu.mem.w_axil_rdata.value}")
        dut._log.info(f"  Data Valid: {dut.cpu.mem.o_Data_Valid.value}")
        dut._log.info(f"  Data: {dut.cpu.mem.o_Data.value}")
        if dut.cpu.mem.o_Data_Valid.value:
            break
    
    result = dut.cpu.reg_file.Registers[1].value.integer
    expected = 0x12345000
    assert result == expected, f"LUI instruction failed: got {result:#010x}, expected {expected:#010x}"
    