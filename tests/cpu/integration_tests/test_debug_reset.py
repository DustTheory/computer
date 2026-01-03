import cocotb
from cpu.utils import uart_send_byte, uart_send_bytes
from cpu.constants import DEBUG_OP_RESET, DEBUG_OP_UNRESET
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

@cocotb.test()
async def test_reset_unreset_cpu (dut):
    """Test debug peripheral reset and unreset functionality"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Set a register to a non-zero value to verify reset works
    dut.cpu.reg_file.Registers[5].value = 0xDEADBEEF

    # Send RESET command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_RESET)
    await ClockCycles(dut.i_Clock, 2)
    assert dut.cpu.debug_peripheral.o_Reset_Cpu.value.integer == 1, "CPU should be in reset after RESET command"

    # Send UNRESET command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNRESET)
    await ClockCycles(dut.i_Clock, 2)
    assert dut.cpu.debug_peripheral.o_Reset_Cpu.value.integer == 0, "CPU should be out of reset after UNRESET command"

    reg_value = dut.cpu.reg_file.Registers[5].value.integer
    assert reg_value == 0, f"CPU registers should be cleared on reset: got {reg_value:#010x}, expected 0x00000000"

