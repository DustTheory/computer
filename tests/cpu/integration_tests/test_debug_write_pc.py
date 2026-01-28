import cocotb
from cpu.utils import uart_send_byte, uart_wait_for_byte, wait_for_pipeline_flush
from cpu.constants import DEBUG_OP_WRITE_PC, DEBUG_OP_READ_PC, DEBUG_OP_UNHALT
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

# Test PC values including edge cases
TEST_PC_VALUES = [
    0x00000000,  # Reset vector
    0x00001000,  # ROM boundary
    0x12345678,  # Typical address
    0xFFFFFFF0,  # Near max address (aligned)
    0x0000BEEF,  # Classic test pattern
    0xCAFEBABE,  # Another test pattern
    0x10203040,  # Incremental pattern
    0x08070605,  # Decremental pattern
]

async def send_write_pc_command(dut, pc_value):
    """Send WRITE_PC command: opcode + 4 PC bytes (little-endian)"""
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_WRITE_PC)

    # Send 4 data bytes in little-endian format
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (pc_value >> 0) & 0xFF)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (pc_value >> 8) & 0xFF)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (pc_value >> 16) & 0xFF)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (pc_value >> 24) & 0xFF)

async def read_pc_value(dut):
    """Read current PC value using READ_PC command"""
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_READ_PC)
    await ClockCycles(dut.i_Clock, 20)  # Wait for command processing

    # Receive 4 bytes in little-endian format
    bytes_received = []
    for _ in range(4):
        byte_val = await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )
        bytes_received.append(byte_val)

    return bytes_received[0] | (bytes_received[1] << 8) | (bytes_received[2] << 16) | (bytes_received[3] << 24)

@cocotb.test()
async def test_write_pc_basic(dut):
    """Test basic WRITE_PC command functionality"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Test writing a specific PC value (WRITE_PC handles halting internally)
    test_pc = 0x12345678

    # Send WRITE_PC command
    await send_write_pc_command(dut, test_pc)
    await ClockCycles(dut.i_Clock, 50)  # Wait for command completion

    # Verify using direct PC access
    direct_pc = dut.cpu.r_PC.value.integer
    assert direct_pc == test_pc, f"WRITE_PC failed: wrote {test_pc:#010x}, PC contains {direct_pc:#010x}"

@cocotb.test()
async def test_write_pc_alignment(dut):
    """Test WRITE_PC with various address alignments"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Test different alignments - RISC-V expects 4-byte aligned but let's test various values
    test_addresses = [
        0x00001000,  # 4-byte aligned
        0x00001001,  # +1 byte (unaligned)
        0x00001002,  # +2 bytes (2-byte aligned)
        0x00001003,  # +3 bytes (unaligned)
        0x00001004,  # Next 4-byte aligned
    ]

    for pc_value in test_addresses:
        await send_write_pc_command(dut, pc_value)
        await ClockCycles(dut.i_Clock, 50)

        # Verify using direct PC access
        direct_pc = dut.cpu.r_PC.value.integer
        assert direct_pc == pc_value, f"Alignment test failed: wrote {pc_value:#010x}, got {direct_pc:#010x}"

@cocotb.test()
async def test_write_pc_data_patterns(dut):
    """Test writing various PC data patterns to ensure correct byte ordering"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i, test_pc in enumerate(TEST_PC_VALUES):
        # Write the PC value (WRITE_PC handles halting internally)
        await send_write_pc_command(dut, test_pc)
        await ClockCycles(dut.i_Clock, 50)

        # Verify using direct PC access
        direct_pc = dut.cpu.r_PC.value.integer
        assert direct_pc == test_pc, f"Pattern {i}: wrote {test_pc:#010x}, got {direct_pc:#010x}"

        # Verify byte ordering by checking individual bytes
        expected_bytes = [
            (test_pc >> 0) & 0xFF,
            (test_pc >> 8) & 0xFF,
            (test_pc >> 16) & 0xFF,
            (test_pc >> 24) & 0xFF,
        ]

        received_bytes = [
            (direct_pc >> 0) & 0xFF,
            (direct_pc >> 8) & 0xFF,
            (direct_pc >> 16) & 0xFF,
            (direct_pc >> 24) & 0xFF,
        ]

        for j, (expected, received) in enumerate(zip(expected_bytes, received_bytes)):
            assert expected == received, f"Pattern {i}, byte {j}: expected {expected:#04x}, got {received:#04x}"
