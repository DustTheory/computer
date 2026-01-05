import cocotb
from cpu.utils import uart_send_byte, uart_wait_for_byte
from cpu.constants import DEBUG_OP_READ_PC, DEBUG_OP_HALT
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

@cocotb.test()
async def test_read_pc_command(dut):
    """Test debug peripheral READ_PC command returns 4 bytes in little-endian format"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Halt CPU to ensure PC is stable
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await ClockCycles(dut.i_Clock, 10)

    # Get the current PC value directly from the CPU
    expected_pc = dut.cpu.r_PC.value.integer
    
    # Send READ_PC command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_READ_PC)
    await ClockCycles(dut.i_Clock, 6)

    # Receive 4 bytes in little-endian format
    byte0 = await uart_wait_for_byte(
        dut.i_Clock,
        dut.cpu.o_Uart_Rx_Out,
        dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
    )

    byte1 = await uart_wait_for_byte(
        dut.i_Clock,
        dut.cpu.o_Uart_Rx_Out,
        dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
    )

    byte2 = await uart_wait_for_byte(
        dut.i_Clock,
        dut.cpu.o_Uart_Rx_Out,
        dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
    )

    byte3 = await uart_wait_for_byte(
        dut.i_Clock,
        dut.cpu.o_Uart_Rx_Out,
        dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
    )

    # Reconstruct PC from little-endian bytes
    received_pc = byte0 | (byte1 << 8) | (byte2 << 16) | (byte3 << 24)

    assert received_pc == expected_pc, f"READ_PC should return current PC value. Expected {expected_pc:#010x}, got {received_pc:#010x}"

    # Verify individual bytes for debugging
    expected_bytes = [
        (expected_pc >> 0) & 0xFF,
        (expected_pc >> 8) & 0xFF,
        (expected_pc >> 16) & 0xFF,
        (expected_pc >> 24) & 0xFF,
    ]
    received_bytes = [byte0, byte1, byte2, byte3]

    for i, (expected, received) in enumerate(zip(expected_bytes, received_bytes)):
        assert expected == received, f"Byte {i} mismatch: expected {expected:#04x}, got {received:#04x}"
