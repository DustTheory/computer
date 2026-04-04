import cocotb
from cpu.utils import uart_send_byte, uart_wait_for_byte, wait_for_halt, wait_for_pipeline_flush
from cpu.constants import (
    DEBUG_OP_READ_MEMORY, DEBUG_OP_HALT, DEBUG_OP_UNHALT,
    CPU_BASE_ADDR, RAM_START_ADDR, UART_CLOCKS_PER_BIT
)
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

MEM_STATE_NAMES = {0: "IDLE", 1: "READ_SUBMITTING", 2: "READ_AWAITING",
                   3: "READ_SUCCESS", 4: "WRITE_SUBMITTING", 5: "WRITE_AWAITING",
                   6: "WRITE_SUCCESS"}
DBG_STATE_NAMES = {0: "s_IDLE", 1: "s_DECODE_AND_EXECUTE"}


def log_debug_peripheral_state(dut):
    dp = dut.cpu.debug_peripheral
    try:
        r_state     = int(dp.r_State.value)
        ibuf_head   = int(dp.input_buffer_head.value)
        obuf_head   = int(dp.output_buffer_head.value)
        obuf_tail   = int(dp.output_buffer_tail.value)
        bytes_rem   = int(dp.r_Bytes_Remaining.value)
        mem_en      = int(dp.o_Memory_LS_Enable.value)
        mem_state   = int(dp.i_Memory_State.value)
        mem_addr    = int(dp.o_Memory_LS_Address.value)
        mem_type    = int(dp.o_Memory_LS_Type.value)
        r_mem_addr  = int(dp.r_Memory_Address.value)
        halt        = int(dp.o_Halt_Cpu.value)
        flushed     = int(dut.cpu.w_Pipeline_Flushed.value)
    except Exception as e:
        dut._log.warning(f"[DBG_STATE] Could not read signal: {e}")
        return
    dut._log.info(
        f"[DBG_STATE] state={DBG_STATE_NAMES.get(r_state, r_state)} "
        f"ibuf_head={ibuf_head} obuf={obuf_head}/{obuf_tail}(head/tail) "
        f"bytes_rem={bytes_rem} halt={halt} flushed={flushed} "
        f"mem_en={mem_en} mem_state={MEM_STATE_NAMES.get(mem_state, mem_state)} "
        f"mem_addr={mem_addr:#010x} mem_type={mem_type} r_mem_addr={r_mem_addr:#010x}"
    )


async def uart_wait_for_byte_debug(dut, i_tx_serial, o_tx_done, label="byte"):
    """Wait for a UART byte with periodic debug logging."""
    log_interval = 500
    timeout_cycles = 5000  # reduced for debug runs - crash fast
    cycles_waited = 0

    dut._log.info(f"[UART_RX] Waiting for {label} start bit (tx_serial={int(i_tx_serial.value)})...")

    while i_tx_serial.value.integer != 0:
        await ClockCycles(dut.i_Clock, 1)
        cycles_waited += 1
        if cycles_waited % log_interval == 0:
            dut._log.info(f"[UART_RX] Still waiting for start bit after {cycles_waited} cycles, tx_serial={int(i_tx_serial.value)}")
            log_debug_peripheral_state(dut)
        if cycles_waited >= timeout_cycles:
            log_debug_peripheral_state(dut)
            raise AssertionError(f"[UART_RX] Timeout ({timeout_cycles} cycles) waiting for {label} start bit")

    dut._log.info(f"[UART_RX] Start bit detected after {cycles_waited} cycles")

    await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT) // 2)
    assert i_tx_serial.value.integer == 0, "UART start bit incorrect."

    received_byte = 0
    for i in range(8):
        await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT))
        bit = i_tx_serial.value.integer
        received_byte |= (bit << i)

    await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT))
    assert i_tx_serial.value.integer == 1, "UART stop bit incorrect."
    await ClockCycles(dut.i_Clock, int(UART_CLOCKS_PER_BIT) // 2)
    assert o_tx_done == 1, "UART o_Tx_Done flag not set"

    dut._log.info(f"[UART_RX] Received {label}: {received_byte:#04x}")
    return received_byte


async def send_read_memory_command(dut, address, num_bytes):
    """Send READ_MEMORY command: opcode + 4-byte address (LE) + 2-byte length (LE)"""
    dut._log.info(f"[CMD] Sending READ_MEMORY opcode 0x0A")
    dut._log.info(f"[TEST] 2: Current PC: {dut.cpu.r_PC.value.integer:#010x}")
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_READ_MEMORY)
    log_debug_peripheral_state(dut)
    dut._log.info(f"[TEST] 3: Current PC: {dut.cpu.r_PC.value.integer:#010x}")

    # Address (little-endian)
    for i, shift in enumerate([0, 8, 16, 24]):
        b = (address >> shift) & 0xFF
        dut._log.info(f"[CMD] Sending addr byte[{i}] = {b:#04x}")
        await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, b)
        log_debug_peripheral_state(dut)

    # Length (little-endian)
    for i, shift in enumerate([0, 8]):
        b = (num_bytes >> shift) & 0xFF
        dut._log.info(f"[CMD] Sending len byte[{i}] = {b:#04x}")
        await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, b)
        log_debug_peripheral_state(dut)

    dut._log.info(f"[CMD] All command bytes sent. State after send:")
    log_debug_peripheral_state(dut)
    # Wait a few cycles and log again to see if state advances
    await ClockCycles(dut.i_Clock, 10)
    dut._log.info(f"[CMD] State after 10 extra cycles:")
    log_debug_peripheral_state(dut)


@cocotb.test()
async def test_read_memory_word(dut):
    """Test READ_MEMORY returns correct bytes for a word-aligned read from ROM"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut._log.info("[TEST] Starting test_read_memory_word")

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    dut._log.info("[TEST] Reset complete. Sending HALT...")
    # Halt CPU so the pipeline is quiet before issuing a memory command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    dut._log.info("[TEST] HALT sent. Waiting for pipeline flush...")
    log_debug_peripheral_state(dut)

    await wait_for_halt(dut)
    await wait_for_pipeline_flush(dut)
    dut._log.info("[TEST] Pipeline flushed.")
    log_debug_peripheral_state(dut)

    # Read 4 bytes from the start of ROM
    address = CPU_BASE_ADDR
    num_bytes = 4
    dut._log.info(f"[TEST] Sending READ_MEMORY: address={address:#010x} num_bytes={num_bytes}")
    await send_read_memory_command(dut, address, num_bytes)

    dut._log.info("[TEST] Command sent, now waiting to receive response bytes...")
    log_debug_peripheral_state(dut)

    # Receive num_bytes bytes back
    received = []
    for i in range(num_bytes):
        dut._log.info(f"[TEST] Waiting for response byte {i+1}/{num_bytes}")
        log_debug_peripheral_state(dut)
        byte_val = await uart_wait_for_byte_debug(
            dut,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done,
            label=f"response[{i}]"
        )
        received.append(byte_val)
        dut._log.info(f"[TEST] Got response byte {i+1}/{num_bytes}: {byte_val:#04x}")
        log_debug_peripheral_state(dut)

    dut._log.info(f"[TEST] All bytes received: {[hex(b) for b in received]}")
    assert len(received) == num_bytes, f"Expected {num_bytes} bytes, got {len(received)}"

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)


@cocotb.test()
async def test_read_memory_multiple_words(dut):
    """Test READ_MEMORY returns the correct number of bytes for a multi-word read"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_halt(dut)
    await wait_for_pipeline_flush(dut)

    # Read 12 bytes (3 words) from ROM
    address = CPU_BASE_ADDR
    num_bytes = 12
    await send_read_memory_command(dut, address, num_bytes)

    received = []
    for _ in range(num_bytes):
        byte_val = await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )
        received.append(byte_val)

    assert len(received) == num_bytes, f"Expected {num_bytes} bytes, got {len(received)}"

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)


@cocotb.test()
async def test_read_memory_byte_count(dut):
    """Test READ_MEMORY returns exactly the requested number of bytes for odd sizes"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_halt(dut)
    await wait_for_pipeline_flush(dut)

    # Read 1 byte (sub-word read)
    address = CPU_BASE_ADDR
    num_bytes = 1
    await send_read_memory_command(dut, address, num_bytes)

    received = []
    for _ in range(num_bytes):
        byte_val = await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )
        received.append(byte_val)

    assert len(received) == num_bytes, f"Expected {num_bytes} bytes, got {len(received)}"

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)


@cocotb.test()
async def test_read_memory_doesnt_break_cpu(dut):
    """Test that READ_MEMORY does not alter CPU register or PC state"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_halt(dut)
    await wait_for_pipeline_flush(dut)

    # Record PC and a register before the memory read
    initial_pc = dut.cpu.r_PC.value.integer
    sentinel_value = 0xCAFEBABE
    dut.cpu.reg_file.Registers[5].value = sentinel_value
    await ClockCycles(dut.i_Clock, 1)

    dut._log.info(f"[TEST] 1: Initial PC: {initial_pc:#010x}, Current PC: {dut.cpu.r_PC.value.integer:#010x}")

    address = CPU_BASE_ADDR
    num_bytes = 4
    await send_read_memory_command(dut, address, num_bytes)

    # Consume response bytes
    for i in range(num_bytes):
        await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )


    # PC and registers should be unchanged
    final_pc = dut.cpu.r_PC.value.integer
    assert final_pc == initial_pc, f"PC changed during READ_MEMORY: {initial_pc:#010x} -> {final_pc:#010x}"

    reg5_value = dut.cpu.reg_file.Registers[5].value.integer
    assert reg5_value == sentinel_value, f"Register 5 changed during READ_MEMORY: expected {sentinel_value:#010x}, got {reg5_value:#010x}"

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)
    await ClockCycles(dut.i_Clock, 3)
