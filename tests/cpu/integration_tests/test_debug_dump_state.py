import cocotb
import struct
from cpu.utils import uart_send_byte, uart_wait_for_byte
from cpu.constants import DEBUG_OP_HALT, DEBUG_OP_DUMP_STATE
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

wait_ns = 1

@cocotb.test()
async def test_dump_state_command(dut):
    """Test DUMP_STATE returns correct 2-byte encoding of pipeline/memory state"""

    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 1)

    # Halt CPU so pipeline state is stable
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_HALT)
    await ClockCycles(dut.i_Clock, 20)

    # Sample expected signal values directly from DUT
    mem_axi_state        = dut.cpu.w_Memory_State.value.integer
    pipeline_flushed     = dut.cpu.w_Pipeline_Flushed.value.integer
    stall_s1             = dut.cpu.w_Stall_S1.value.integer
    enable_fetch         = dut.cpu.w_Enable_Instruction_Fetch.value.integer
    s2_valid             = dut.cpu.r_S2_Valid.value.integer
    s3_valid             = dut.cpu.r_S3_Valid.value.integer
    instr_mem_axi_state  = dut.cpu.w_Instruction_Memory_State.value.integer
    init_calib_complete  = dut.cpu.i_Init_Calib_Complete.value.integer

    expected_byte0 = (
        ((mem_axi_state & 0x7) << 5) |
        ((pipeline_flushed & 0x1) << 4) |
        ((stall_s1 & 0x1) << 3) |
        ((enable_fetch & 0x1) << 2) |
        ((s2_valid & 0x1) << 1) |
        (s3_valid & 0x1)
    )
    expected_byte1 = (
        ((instr_mem_axi_state & 0x3) << 6) |
        ((init_calib_complete & 0x1) << 5)
    )

    # Send DUMP_STATE command
    await uart_send_byte(dut.i_Clock, dut.cpu.i_Uart_Tx_In, dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV, DEBUG_OP_DUMP_STATE)
    await ClockCycles(dut.i_Clock, 6)

    # Receive 2-byte response
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

    assert byte0 == expected_byte0, (
        f"DUMP_STATE byte0 mismatch. Expected 0x{expected_byte0:02X}, got 0x{byte0:02X}\n"
        f"  mem_axi={mem_axi_state}, pipeline_flushed={pipeline_flushed}, "
        f"stall_s1={stall_s1}, enable_fetch={enable_fetch}, "
        f"s2_valid={s2_valid}, s3_valid={s3_valid}"
    )
    assert byte1 == expected_byte1, (
        f"DUMP_STATE byte1 mismatch. Expected 0x{expected_byte1:02X}, got 0x{byte1:02X}\n"
        f"  instr_mem_axi={instr_mem_axi_state}, init_calib_complete={init_calib_complete}"
    )

    # Verify individual fields from byte0
    assert ((byte0 >> 5) & 0x7) == mem_axi_state, "data mem_axi_state mismatch"
    assert ((byte0 >> 4) & 0x1) == pipeline_flushed, "pipeline_flushed mismatch"
    assert ((byte0 >> 3) & 0x1) == stall_s1, "stall_s1 mismatch"
    assert ((byte0 >> 2) & 0x1) == enable_fetch, "enable_fetch mismatch"
    assert ((byte0 >> 1) & 0x1) == s2_valid, "s2_valid mismatch"
    assert (byte0 & 0x1) == s3_valid, "s3_valid mismatch"

    # Verify individual fields from byte1
    assert ((byte1 >> 6) & 0x3) == instr_mem_axi_state, "instr_mem_axi_state mismatch"
    assert ((byte1 >> 5) & 0x1) == init_calib_complete, "init_calib_complete mismatch"

    # Read 56 perf counter bytes (7 x 64-bit little-endian)
    perf_bytes = []
    for _ in range(56):
        b = await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )
        perf_bytes.append(b)

    cycles               = struct.unpack_from('<Q', bytes(perf_bytes[0:8]))[0]
    instructions_retired = struct.unpack_from('<Q', bytes(perf_bytes[8:16]))[0]
    stall_cycles_load    = struct.unpack_from('<Q', bytes(perf_bytes[16:24]))[0]
    stall_cycles_store   = struct.unpack_from('<Q', bytes(perf_bytes[24:32]))[0]
    stall_cycles_fetch   = struct.unpack_from('<Q', bytes(perf_bytes[32:40]))[0]
    flush_cycles         = struct.unpack_from('<Q', bytes(perf_bytes[40:48]))[0]
    mem_errors           = struct.unpack_from('<Q', bytes(perf_bytes[48:56]))[0]

    # i_Init_Calib_Complete = 1 in harness so cycles must be > 0
    assert cycles > 0, f"cycles should be > 0, got {cycles}"
    # No bad AXI responses in test harness
    assert mem_errors == 0, f"mem_errors should be 0, got {mem_errors}"
    # Stall counters must not exceed total cycles
    assert stall_cycles_load  <= cycles, f"stall_cycles_load {stall_cycles_load} > cycles {cycles}"
    assert stall_cycles_store <= cycles, f"stall_cycles_store {stall_cycles_store} > cycles {cycles}"
    assert stall_cycles_fetch <= cycles, f"stall_cycles_fetch {stall_cycles_fetch} > cycles {cycles}"
    assert flush_cycles       <= cycles, f"flush_cycles {flush_cycles} > cycles {cycles}"
