import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

from cpu.constants import UART_CLOCKS_PER_BIT
from cpu.utils import uart_wait_for_byte

@cocotb.test()
async def test_uart_transmitter_send_byte_bit_by_bit(dut):
    """Test UART transmitter by sending a byte and verifying the serial output."""

    wait_ns = 1

    # Reset the debug peripheral
    dut.i_Reset.value = 1
    dut.i_Clock.value = 1
    await Timer(100, units="ns")
    dut.i_Reset.value = 0
    dut.i_Clock.value = 0
    await Timer(100, units="ns")

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    test_byte = 0x5A  # 01011010

    # Queue the byte for transmission
    dut.uart_transmitter.i_Tx_Byte.value = test_byte
    dut.uart_transmitter.i_Tx_DV.value = 1
    await ClockCycles(dut.i_Clock, 2)
    dut.uart_transmitter.i_Tx_DV.value = 0

    assert dut.uart_transmitter.r_SM_Main.value.integer != 0, "UART Transmitter did not start transmission state machine."
    assert dut.uart_transmitter.r_Tx_Byte.value.integer == test_byte, "UART Transmitter did not load the correct byte." 
    assert dut.uart_transmitter.o_Tx_Done.value.integer == 0, "UART Transmitter should not be done immediately after starting transmission."

    await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT) - 1)
    assert dut.uart_transmitter.o_Tx_Serial.value.integer == 0, f"UART Transmitter start bit incorrect: got {actual_bit}, expected 0"
    await ClockCycles(dut.i_Clock, 1)

    # Data bits (LSB first)
    for i in range(8):
        expected_bit = (test_byte >> i) & 0x1
        for j in range(int(UART_CLOCKS_PER_BIT)):
            await ClockCycles(dut.i_Clock, 1)
            if j == int(UART_CLOCKS_PER_BIT) - 1:
                actual_bit = dut.uart_transmitter.o_Tx_Serial.value.integer
                assert actual_bit == expected_bit, f"UART Transmitter bit {i} incorrect: got {actual_bit}, expected {expected_bit}"

    # Stop bit
    for i in range(int(UART_CLOCKS_PER_BIT)):
        await ClockCycles(dut.i_Clock, 1)
        if i == int(UART_CLOCKS_PER_BIT) - 1:
            actual_bit = dut.uart_transmitter.o_Tx_Serial.value.integer
            assert actual_bit == 1, f"UART Transmitter stop bit incorrect: got {actual_bit}, expected 1"
            dut._log.info("Stop bit sent correctly: %d", actual_bit)

    # Wait for transmission to complete
    for i in range(100):  # Arbitrary large number to ensure completion
        await ClockCycles(dut.i_Clock, 1)
        if dut.uart_transmitter.o_Tx_Done.value.integer == 1:
            dut._log.info("Transmission done after %d clock cycles.", i+1)
            break
    else:
        assert False, "UART Transmitter did not assert Tx_Done after transmission."

@cocotb.test()
async def test_uart_transmitter_send_byte(dut):
    """Test UART transmitter by sending a byte and verifying the serial output."""

    wait_ns = 1

    # Reset the debug peripheral
    dut.i_Reset.value = 1
    dut.i_Clock.value = 1
    await Timer(100, units="ns")
    dut.i_Reset.value = 0
    dut.i_Clock.value = 0
    await Timer(100, units="ns")

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())
    wait_for_byte_task = cocotb.start_soon(uart_wait_for_byte(dut.i_Clock, dut.uart_transmitter.o_Tx_Serial, dut.uart_transmitter.o_Tx_Done))
    
    test_byte = 0xA5  # 10100101

    # Queue the byte for transmission
    dut.uart_transmitter.i_Tx_Byte.value = test_byte
    dut.uart_transmitter.i_Tx_DV.value = 1

    await ClockCycles(dut.i_Clock, 1)
    dut.uart_transmitter.i_Tx_DV.value = 0

    received_byte = await wait_for_byte_task
    assert received_byte == test_byte, f"UART Transmitter did not send correct byte: got {bin(received_byte)}, expected {bin(test_byte)}"
    