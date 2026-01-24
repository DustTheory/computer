import cocotb
from cpu.utils import uart_send_byte, uart_wait_for_byte, wait_for_pipeline_flush
from cpu.constants import DEBUG_OP_READ_REGISTER, DEBUG_OP_WRITE_REGISTER, DEBUG_OP_HALT, DEBUG_OP_UNHALT
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

# Test multiple registers now that full implementation is ready
REGISTERS_TO_TEST = [0, 1, 2, 5, 10, 31]  # Test representative registers including edge cases

@cocotb.test()
async def test_read_register_basic(dut):
    """Test debug peripheral READ_REGISTER command with register address parameter"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # HALT CPU before setup
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    # Test with register 1 for basic functionality
    test_register = 1
    test_value = 0xDEADBEEF
    dut.cpu.reg_file.Registers[test_register].value = test_value

    # Wait a cycle for the value to propagate in simulation
    await ClockCycles(dut.i_Clock, 1)

    # Get the expected value (while CPU is still halted)
    expected_reg_value = dut.cpu.reg_file.Registers[test_register].value.integer

    # Send READ_REGISTER command (CPU is already halted, no need to UNHALT first)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_READ_REGISTER)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, test_register)
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

    # Reconstruct register value from little-endian bytes
    received_reg_value = byte0 | (byte1 << 8) | (byte2 << 16) | (byte3 << 24)

    assert received_reg_value == expected_reg_value, f"READ_REGISTER should return register 1 value. Expected {expected_reg_value:#010x}, got {received_reg_value:#010x}"

    # UNHALT CPU at the end to restore normal state
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)

    # Verify individual bytes for debugging
    expected_bytes = [
        (expected_reg_value >> 0) & 0xFF,
        (expected_reg_value >> 8) & 0xFF,
        (expected_reg_value >> 16) & 0xFF,
        (expected_reg_value >> 24) & 0xFF,
    ]
    received_bytes = [byte0, byte1, byte2, byte3]

    for i, (expected, received) in enumerate(zip(expected_bytes, received_bytes)):
        assert expected == received, f"Byte {i} mismatch: expected {expected:#04x}, got {received:#04x}"

@cocotb.test()
async def test_read_register_doesnt_break_cpu(dut):
    """Test that READ_REGISTER command doesn't affect CPU state or register values"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # HALT CPU before setup
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    # Set multiple registers to known values
    test_values = {
        1: 0x11111111,
        2: 0x22222222,
        3: 0x33333333,
        31: 0xFFFFFFFF
    }

    for reg_addr, value in test_values.items():
        dut.cpu.reg_file.Registers[reg_addr].value = value

    # Save PC before command
    initial_pc = dut.cpu.r_PC.value.integer

    # Send READ_REGISTER command (CPU is already halted, no need to UNHALT first)
    # Test with register 2
    test_register = 2
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_READ_REGISTER)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, test_register)
    await ClockCycles(dut.i_Clock, 6)

    # Consume the 4 response bytes (don't need to verify content here)
    for _ in range(4):
        await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )

    # Verify all register values unchanged (CPU still halted)
    for reg_addr, expected_value in test_values.items():
        current_value = dut.cpu.reg_file.Registers[reg_addr].value.integer
        assert current_value == expected_value, f"Register {reg_addr} changed! Expected {expected_value:#010x}, got {current_value:#010x}"

    # UNHALT CPU at the end to restore normal state
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)



@cocotb.test()
async def test_read_register_loop_ready(dut):
    """Test reading multiple registers using the loop structure"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # HALT CPU before setup
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    # Test data for each register
    test_data = {
        0: 0x00000000,  # Register 0 should always be 0 (will test this)
        1: 0x12345678,
        2: 0x87654321,
        5: 0xDEADBEEF,
        10: 0xCAFEBABE,
        31: 0xFFFFFFFF
    }

    # Set all test registers upfront while CPU is halted
    for reg_addr in REGISTERS_TO_TEST:
        test_value = test_data.get(reg_addr, 0xABCDEF00 + reg_addr)
        if reg_addr != 0:  # Can't write to register 0 in RISC-V
            dut.cpu.reg_file.Registers[reg_addr].value = test_value

    # CPU stays halted throughout test - READ_REGISTER works with halted CPU

    for reg_addr in REGISTERS_TO_TEST:
        # Get expected value (register 0 is always 0, others should be test_value)
        expected_value = 0 if reg_addr == 0 else test_data.get(reg_addr, 0xABCDEF00 + reg_addr)

        # Send READ_REGISTER command: opcode + register address
        await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_READ_REGISTER)
        await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, reg_addr)
        await ClockCycles(dut.i_Clock, 6)

        # Receive 4 bytes
        bytes_received = []
        for _ in range(4):
            byte_val = await uart_wait_for_byte(
                dut.i_Clock,
                dut.cpu.o_Uart_Rx_Out,
                dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
            )
            bytes_received.append(byte_val)

        # Reconstruct value
        received_value = bytes_received[0] | (bytes_received[1] << 8) | (bytes_received[2] << 16) | (bytes_received[3] << 24)

        # Verify the register was read correctly
        assert received_value == expected_value, f"Register {reg_addr}: expected {expected_value:#010x}, got {received_value:#010x}"

    # UNHALT CPU at the end to restore normal state
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)