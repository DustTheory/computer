import cocotb
from cocotb.triggers import ClockCycles
from cocotb.clock import Clock
from cpu.utils import uart_send_bytes, uart_send_byte
from cpu.constants import CLOCK_FREQUENCY, UART_CLOCKS_PER_BIT

wait_ns = 1

@cocotb.test()
async def test_uart_receiver_byte_bit_by_bit(dut):
    """Test basic UART receiver functionality of the debug peripheral."""

    # Reset the debug peripheral
    dut.i_Reset.value = 1
    await cocotb.triggers.Timer(100, units="ns")
    dut.i_Reset.value = 0
    await cocotb.triggers.Timer(100, units="ns")

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    test_byte = 0xA5  # 10100101

    # Start bit
    dut.uart_receiver.i_Rx_Serial.value = 0
    await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT))
    dut._log.info("State after start bit sent: r_SM_Main=%d Rx_DV=%d, Rx_Byte=0x%02X", dut.uart_receiver.r_SM_Main.value.integer, dut.uart_receiver.o_Rx_DV.value.integer, dut.uart_receiver.o_Rx_Byte.value.integer)
    assert dut.uart_receiver.r_SM_Main.value.integer == 2, "UART Receiver did not enter DATA_BITS state after start bit."

    # Data bits (LSB first)
    for i in range(8):
        dut.uart_receiver.i_Rx_Serial.value = (test_byte >> i) & 0x1
        await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT))
        assert dut.uart_receiver.o_Rx_Byte.value.integer == (test_byte & ((1 << (i + 1)) - 1)), f"UART Receiver byte incorrect after bit {i}."
        dut._log.info("State after bit %d sent: r_SM_Main=%d Rx_DV=%d, Rx_Byte=0x%02X", i, dut.uart_receiver.r_SM_Main.value.integer, dut.uart_receiver.o_Rx_DV.value.integer, dut.uart_receiver.o_Rx_Byte.value.integer)


    assert dut.uart_receiver.r_SM_Main.value.integer == 3, "UART Receiver did not enter STOP_BIT state after data bits."

    # Sometime in the next bit time, Rx_DV should be asserted
    for i in range(int(UART_CLOCKS_PER_BIT)):
        await ClockCycles(dut.i_Clock, 1)
        if dut.uart_receiver.o_Rx_DV.value.integer == 1:
            dut._log.info("o_Rx_DV asserted after %d clock cycles in stop bit.", i+1)
            break
    else:
        assert False, "UART Receiver did not assert Rx_DV after receiving byte."

    assert dut.uart_receiver.o_Rx_Byte.value.integer == test_byte, f"UART Receiver byte incorrect: got 0x{dut.uart_receiver.o_Rx_Byte.value.integer:02X}, expected 0x{test_byte:02X}"

@cocotb.test()
async def test_uart_receiver_send_byte(dut):
    """Test UART receiver with multiple bytes sent in sequence."""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    test_byte = 0x3C  # 00111100

    await uart_send_byte(dut.i_Clock, dut.uart_receiver.i_Rx_Serial, dut.uart_receiver.o_Rx_DV, test_byte)
    assert dut.uart_receiver.o_Rx_Byte.value.integer == test_byte, f"UART Receiver byte incorrect: got 0x{dut.uart_receiver.o_Rx_Byte.value.integer:02X}, expected 0x{test_byte:02X}"
    assert dut.uart_receiver.o_Rx_DV.value.integer == 1, "UART Receiver did not assert Rx_DV after receiving byte."

@cocotb.test()
async def test_uart_receiver_send_bytes(dut):
    """Test UART receiver with multiple bytes sent in sequence."""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    test_bytes = [0x55, 0xAA, 0xFF, 0x00, 0x7E]

    await uart_send_bytes(dut.i_Clock, dut.uart_receiver.i_Rx_Serial, dut.uart_receiver.o_Rx_DV, test_bytes)

    assert dut.uart_receiver.o_Rx_Byte.value.integer == test_bytes[-1], f"UART Receiver byte incorrect: got 0x{dut.uart_receiver.o_Rx_Byte.value.integer:02X}, expected 0x{test_bytes[-1]:02X}"
