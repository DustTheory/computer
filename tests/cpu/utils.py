from cpu.constants import (
    CLOCK_FREQUENCY,
    OP_B_TYPE,
    OP_S_TYPE,
    OP_R_TYPE,

    ROM_BOUNDARY_ADDR,
    
    UART_CLOCKS_PER_BIT,
)
from cocotb.triggers import ClockCycles, FallingEdge

def gen_i_type_instruction(opcode, rd, funct3, rs1, imm):
    instruction = opcode
    instruction |= rd << 7
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= (imm & 0b111111111111) << 20
    return instruction

def gen_b_type_instruction(funct3, rs1, rs2, offset):
    opcode = OP_B_TYPE
    instruction = opcode
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= rs2 << 20

    imm_12 = (offset >> 12) & 0x1
    imm_10_5 = (offset >> 5) & 0x3F
    imm_4_1 = (offset >> 1) & 0xF
    imm_11 = (offset >> 11) & 0x1

    instruction |= imm_11 << 7
    instruction |= imm_4_1 << 8
    instruction |= imm_10_5 << 25
    instruction |= imm_12 << 31

    return instruction

def gen_s_type_instruction(funct3, rs1, rs2, imm):
    opcode = OP_S_TYPE
    instruction = opcode
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= rs2 << 20

    imm_4_0 = imm & 0b11111
    imm_11_5 = (imm >> 5) & 0b1111111

    instruction |= imm_4_0 << 7
    instruction |= imm_11_5 << 25

    return instruction

def gen_r_type_instruction(rd, funct3, rs1, rs2, funct7):
    instruction = OP_R_TYPE
    instruction |= rd << 7
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= rs2 << 20
    instruction |= funct7 << 25
    return instruction

def write_word_to_mem(mem_array, addr, value):
    """Write a 32-bit value into byte-addressable cocotb memory (little-endian)."""
    mem_array[addr + 0].value = (value >> 0) & 0xFF
    mem_array[addr + 1].value = (value >> 8) & 0xFF
    mem_array[addr + 2].value = (value >> 16) & 0xFF
    mem_array[addr + 3].value = (value >> 24) & 0xFF

def write_half_to_mem(mem_array, addr, value):
    mem_array[addr + 0].value = (value >> 0) & 0xFF
    mem_array[addr + 1].value = (value >> 8) & 0xFF

def write_byte_to_mem(mem_array, addr, value):
    mem_array[addr].value = value & 0xFF

def write_instructions(mem_array, base_addr, instructions):
    """Write a list of 32-bit instructions at word stride (4 bytes)."""
    if base_addr < ROM_BOUNDARY_ADDR:
        raise ValueError(f"Base address {base_addr:#06x} is inside of ROM boundary.")
    for i, ins in enumerate(instructions):
        write_word_to_mem(mem_array, base_addr + 4*i, ins)

def write_instructions_rom(mem_array, base_addr, instructions):
    if base_addr > ROM_BOUNDARY_ADDR:
        raise ValueError(f"Base address {base_addr:#06x} is outside of ROM boundary.")
    for i, ins in enumerate(instructions):
        mem_array[base_addr//4 + i].value = ins


async def uart_send_byte(clock, i_rx_serial, o_rx_dv, data_byte):
    """Send bytes over UART RX line bit by bit."""

    i_rx_serial.value = 0
    await ClockCycles(clock, int(UART_CLOCKS_PER_BIT))

    # Data bits (LSB first)
    for i in range(8):
        i_rx_serial.value = (data_byte >> i) & 0x1
        await ClockCycles(clock, int(UART_CLOCKS_PER_BIT))

    # Stop bit
    i_rx_serial.value = 1
    for _ in range(int(UART_CLOCKS_PER_BIT)):
        if o_rx_dv.value.integer == 1:
            break
        await ClockCycles(clock, 1)


async def uart_send_bytes(clock, i_rx_serial, o_rx_dv, byte_array):
    """Send bytes over UART RX line bit by bit."""
    for byte in byte_array:
        await uart_send_byte(clock, i_rx_serial, o_rx_dv, byte)
        await FallingEdge(o_rx_dv)  # Wait for Rx_DV to go low before sending next byte

async def uart_wait_for_byte(clock, i_tx_serial, o_tx_done):
    """Wait for a byte to be transmitted over UART TX line bit by bit."""

    # Wait for start bit for max 1 second
    timeout_cycles = CLOCK_FREQUENCY  # 1 second timeout
    cycles_waited = 0
    while i_tx_serial.value.integer != 0:
        await ClockCycles(clock, 1)
        cycles_waited += 1
        assert cycles_waited < timeout_cycles, "Timeout waiting for UART start bit."

    # Wait UART_CLOCKS_PER_BIT/2 to sample in middle of start bit
    await ClockCycles(clock, int(UART_CLOCKS_PER_BIT) // 2)
    assert i_tx_serial.value.integer == 0, "UART start bit incorrect."

    # Data bits (LSB first)
    received_byte = 0
    for i in range(8):
        await ClockCycles(clock, int(UART_CLOCKS_PER_BIT))
        bit = i_tx_serial.value.integer
        received_byte |= (bit << i)

    # Wait to middle of stop bit and check
    await ClockCycles(clock, int(UART_CLOCKS_PER_BIT))
    assert i_tx_serial.value.integer == 1, "UART stop bit incorrect."

    # Wait for rest of stop bit
    await ClockCycles(clock, int(UART_CLOCKS_PER_BIT)//2)

    assert o_tx_done == 1, "UART o_Tx_Done flag not set"

    return received_byte

async def wait_for_pipeline_flush(dut, timeout_cycles=1000):
    """
    Wait for CPU pipeline to flush (becomes empty).
    Required after HALT command before setting up CPU state.

    Args:
        dut: The test harness DUT
        timeout_cycles: Maximum cycles to wait

    Raises:
        AssertionError: If pipeline doesn't flush within timeout
    """
    for i in range(timeout_cycles):
        if dut.cpu.w_Pipeline_Flushed.value == 1:
            return
        await ClockCycles(dut.i_Clock, 1)
    raise AssertionError(f"Pipeline did not flush after {timeout_cycles} cycles")

