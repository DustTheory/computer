import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer
from cpu.utils import uart_send_byte, uart_wait_for_byte
from cpu.constants import DEBUG_OP_HALT, DEBUG_OP_UNHALT, DEBUG_OP_RESET, DEBUG_OP_UNRESET, PING_RESPONSE_BYTE, DEBUG_OP_PING

wait_ns = 1

@cocotb.test()
async def test_halt_unhalt_cpu (dut):
    """Test debug peripheral halt and unhalt functionality"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await Timer(100, units="ns")
    dut.i_Reset.value = 0
    await Timer(100, units="ns")

    # Send HALT command
    await uart_send_byte(dut.i_Clock, dut.debug_peripheral.i_Uart_Tx_In, dut.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)

    dut._log.info("Debug peripheral state after HALT command: r_State=%d, r_Op_Code=0x%02X, r_Exec_Counter=%d", dut.debug_peripheral.r_State.value.integer, dut.debug_peripheral.r_Op_Code.value.integer, dut.debug_peripheral.r_Exec_Counter.value.integer)
    dut._log.info("Debug peripheral uart receiver state: r_SM_Main=%d, Rx_DV=%d, Rx_Byte=0x%02X", dut.debug_peripheral.uart_receiver.r_SM_Main.value.integer, dut.debug_peripheral.uart_receiver.o_Rx_DV.value.integer, dut.debug_peripheral.uart_receiver.o_Rx_Byte.value.integer)
    await ClockCycles(dut.i_Clock, 1)
    dut._log.info("Debug peripheral state 1 cycle after HALT command: r_State=%d, r_Op_Code=0x%02X, r_Exec_Counter=%d", dut.debug_peripheral.r_State.value.integer, dut.debug_peripheral.r_Op_Code.value.integer, dut.debug_peripheral.r_Exec_Counter.value.integer)
    dut._log.info("Debug peripheral uart receiver state: r_SM_Main=%d, Rx_DV=%d, Rx_Byte=0x%02X", dut.debug_peripheral.uart_receiver.r_SM_Main.value.integer, dut.debug_peripheral.uart_receiver.o_Rx_DV.value.integer, dut.debug_peripheral.uart_receiver.o_Rx_Byte.value.integer)
    await ClockCycles(dut.i_Clock, 1)
    dut._log.info("Debug peripheral state 2 cycles after HALT command: r_State=%d, r_Op_Code=0x%02X, r_Exec_Counter=%d", dut.debug_peripheral.r_State.value.integer, dut.debug_peripheral.r_Op_Code.value.integer, dut.debug_peripheral.r_Exec_Counter.value.integer)
    await ClockCycles(dut.i_Clock, 10)
    assert dut.debug_peripheral.o_Halt_Cpu.value.integer == 1, "CPU should be halted after HALT command"

    # Send UNHALT command
    await uart_send_byte(dut.i_Clock, dut.debug_peripheral.i_Uart_Tx_In, dut.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 10)
    assert dut.debug_peripheral.o_Halt_Cpu.value.integer == 0, "CPU should be unhalted after UNHALT command"

@cocotb.test()
async def test_reset_unreset_cpu (dut):
    """Test debug peripheral reset and unreset functionality"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await Timer(100, units="ns")
    dut.i_Reset.value = 0
    await Timer(100, units="ns")

    # Send RESET command
    await uart_send_byte(dut.i_Clock, dut.debug_peripheral.i_Uart_Tx_In, dut.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_RESET)
    await ClockCycles(dut.i_Clock, 10)
    assert dut.debug_peripheral.o_Reset_Cpu.value.integer == 1, "CPU should be in reset after RESET command"

    # Send UNRESET command
    await uart_send_byte(dut.i_Clock, dut.debug_peripheral.i_Uart_Tx_In, dut.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNRESET)
    await ClockCycles(dut.i_Clock, 10)
    assert dut.debug_peripheral.o_Reset_Cpu.value.integer == 0, "CPU should be out of reset after UNRESET command"  

@cocotb.test()
async def test_ping_command (dut):
    """Test debug peripheral PING command functionality"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await Timer(100, units="ns")
    dut.i_Reset.value = 0
    await Timer(100, units="ns")

    # Start task to wait for byte from UART transmitter
    wait_for_byte_task = cocotb.start_soon(uart_wait_for_byte(dut.i_Clock, dut.debug_peripheral.uart_transmitter.o_Tx_Serial, dut.debug_peripheral.uart_transmitter.o_Tx_Done))

    # Send PING command
    await uart_send_byte(dut.i_Clock, dut.debug_peripheral.i_Uart_Tx_In, dut.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_PING) 

    received_byte = await wait_for_byte_task
    assert received_byte == PING_RESPONSE_BYTE, f"Debug peripheral did not respond correctly to PING command: got {bin(received_byte)}, expected {bin(PING_RESPONSE_BYTE)}"