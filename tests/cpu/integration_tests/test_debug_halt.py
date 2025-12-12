import cocotb
from cpu.utils import uart_send_byte, uart_send_bytes
from cpu.constants import DEBUG_OP_HALT, DEBUG_OP_UNHALT, DEBUG_OP_RESET, DEBUG_OP_UNRESET
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge


wait_ns = 1

@cocotb.test()
async def test_halt_unhalt_cpu (dut):
    """Test debug peripheral halt and unhalt functionality"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Send HALT command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await ClockCycles(dut.i_Clock, 2)
    old_pc = dut.cpu.r_PC.value.integer
    assert dut.cpu.debug_peripheral.o_Halt_Cpu.value.integer == 1, "CPU should be halted after HALT command"

    await ClockCycles(dut.i_Clock, 100)
    assert dut.cpu.r_PC.value.integer == old_pc, f"CPU PC should not change when halted: old PC={old_pc:#010x}, new PC={dut.cpu.r_PC.value.integer:#010x}"

    # Send UNHALT command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 2)
    assert dut.cpu.debug_peripheral.o_Halt_Cpu.value.integer == 0, "CPU should be unhalted after UNHALT command"

    await ClockCycles(dut.i_Clock, 100)
    assert dut.cpu.r_PC.value.integer != old_pc, f"CPU PC should change when unhalted: old PC={old_pc:#010x}, new PC={dut.cpu.r_PC.value.integer:#010x}"
