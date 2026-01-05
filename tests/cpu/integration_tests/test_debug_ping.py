import cocotb
from cpu.utils import uart_send_byte, uart_wait_for_byte
from cpu.constants import DEBUG_OP_PING, PING_RESPONSE_BYTE
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

@cocotb.test()
async def test_ping_response(dut):
    """Test debug peripheral PING command returns 0xAA"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Send PING command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_PING)
    await ClockCycles(dut.i_Clock, 2)

    # Wait for and receive response byte
    response_byte = await uart_wait_for_byte(
        dut.i_Clock,
        dut.cpu.o_Uart_Rx_Out,
        dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
    )

    assert response_byte == PING_RESPONSE_BYTE, f"PING response should be 0xAA, got {response_byte:#04x}"
