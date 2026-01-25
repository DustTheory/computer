import cocotb
from cocotb.triggers import RisingEdge, ClockCycles
from cocotb.clock import Clock

from cpu.utils import wait_for_pipeline_flush, write_instructions_rom, write_word_to_mem, write_instructions, uart_send_byte
from cpu.constants import CPU_BASE_ADDR, DEBUG_OP_HALT, DEBUG_OP_UNHALT, DEBUG_OP_WRITE_PC, RAM_START_ADDR, ROM_BOUNDARY_ADDR

wait_ns = 1

@cocotb.test()
async def test_single_instruction_fetch_dram(dut):
    """Test instruction fetch from instruction memory (dram)"""
    dut._log.info("Starting instruction fetch test")

    test_instruction = 0x12345678
    write_word_to_mem(dut.instruction_ram.mem, RAM_START_ADDR, test_instruction)
    write_word_to_mem(dut.instruction_ram.mem, RAM_START_ADDR + 4, 0x9ABCDEF0)
    write_word_to_mem(dut.instruction_ram.mem, RAM_START_ADDR + 8, 0x0FEDCBA9)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0

    # HALT CPU before setup
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    dut.cpu.r_PC.value = RAM_START_ADDR

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)

    await RisingEdge(dut.cpu.w_Instruction_Valid)

    fetched_instruction = dut.cpu.w_Instruction.value.integer
    assert fetched_instruction == test_instruction, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {test_instruction:#010x}"

@cocotb.test()
async def test_single_instruction_fetch_rom(dut):
    """Test instruction fetch from instruction memory (rom)"""
    dut._log.info("Starting instruction fetch test")

    test_instruction = 0x12345678
    write_instructions_rom(dut.cpu.instruction_memory.rom, CPU_BASE_ADDR, [test_instruction, 0x9ABCDEF0, 0x0FEDCBA9])

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0

    await RisingEdge(dut.cpu.w_Instruction_Valid)

    fetched_instruction = dut.cpu.w_Instruction.value.integer
    assert fetched_instruction == test_instruction, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {test_instruction:#010x}"


@cocotb.test()
async def test_multiple_instruction_fetch_dram(dut):
    """Test fetching multiple instructions from instruction_memory (dram)"""
    dut._log.info("Starting multiple instruction fetch test")

    instructions = [
        0x12345678,
        0xABADBABE,
        0xB16B00B5,
    ]

    write_instructions(dut.instruction_ram.mem, RAM_START_ADDR, instructions)
    dut._log.info(f"Wrote instructions to DRAM at address {RAM_START_ADDR:#010x}")
    dut._log.info(f"Instruction 0: {dut.instruction_ram.mem[0x1000].value.integer:#04x} {dut.instruction_ram.mem[0x1001].value.integer:#04x} {dut.instruction_ram.mem[0x1002].value.integer:#04x} {dut.instruction_ram.mem[0x1003].value.integer:#04x}")
    dut._log.info(f"Instruction 1: {dut.instruction_ram.mem[0x1004].value.integer:#04x} {dut.instruction_ram.mem[0x1005].value.integer:#04x} {dut.instruction_ram.mem[0x1006].value.integer:#04x} {dut.instruction_ram.mem[0x1007].value.integer:#04x}")
    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # HALT CPU before setup
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_WRITE_PC)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (RAM_START_ADDR >> 0) & 0xFF)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (RAM_START_ADDR >> 8) & 0xFF)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (RAM_START_ADDR >> 16) & 0xFF)
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, (RAM_START_ADDR >> 24) & 0xFF)

    await ClockCycles(dut.i_Clock, 10)

    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_UNHALT)

    for i in range(1):
        await RisingEdge(dut.cpu.w_Instruction_Valid)
        dut._log.info(f"Program Counter: {dut.cpu.r_PC.value.integer:#010x}")
        dut._log.info(f"Fetched instruction {i}: {dut.cpu.w_Instruction.value.integer:#010x}")
        dut._log.info(f"Instruction Valid: {dut.cpu.w_Instruction_Valid.value}")

        fetched_instruction = dut.cpu.w_Instruction.value.integer
        expected = instructions[i]
        assert fetched_instruction == expected, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {expected:#010x}"

@cocotb.test()
async def test_multiple_instruction_fetch_rom(dut):
    """Test fetching multiple instructions from instruction_memory (rom)"""
    dut._log.info("Starting multiple instruction fetch test")

    instructions = [
        0x12345678,
        0xABADBABE,
        0xB16B00B5,
    ]

    write_instructions_rom(dut.cpu.instruction_memory.rom, CPU_BASE_ADDR, instructions)

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    for i in range(1):
        await RisingEdge(dut.cpu.w_Instruction_Valid)
        dut._log.info(f"Fetched instruction {i}: {dut.cpu.w_Instruction.value.integer:#010x}")
        dut._log.info(f"Instruction Valid: {dut.cpu.w_Instruction_Valid.value}")

        fetched_instruction = dut.cpu.w_Instruction.value.integer
        expected = instructions[i]
        assert fetched_instruction == expected, f"Instruction fetch failed: got {fetched_instruction:#010x}, expected {expected:#010x}"
