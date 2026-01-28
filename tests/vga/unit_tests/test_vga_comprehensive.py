import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from cocotb.utils import get_sim_time
from vga.constants import *
from vga.utils import pack_rgb, drive_vdma_stream

import time


async def wait_pixel_tick(dut):
    """Wait for the VGA pixel clock tick (every 4 system clocks)."""
    while True:
        await RisingEdge(dut.i_Clock)
        if int(dut.vga_out.r_Clock_Counter.value) == 0:
            return


async def wait_for_fsync_rising(dut):
    """Wait for a rising edge of the fsync level (robust against multi-cycle high)."""
    while int(dut.o_mm2s_fsync.value) == 1:
        await RisingEdge(dut.i_Clock)
    while True:
        await RisingEdge(dut.i_Clock)
        if int(dut.o_mm2s_fsync.value) == 1:
            return


async def wait_for_fsync_event(dut):
    """Treat an already-high fsync as an event; otherwise wait for rising."""
    if int(dut.o_mm2s_fsync.value) == 1:
        return
    await wait_for_fsync_rising(dut)


def pattern_pixel(x, y):
    red = x & 0xF
    green = (x + y) & 0xF
    blue = y & 0xF
    return pack_rgb(red, green, blue)


def pattern_expected(x, y):
    return (x & 0xF), ((x + y) & 0xF), (y & 0xF)

@cocotb.test()
async def test_vga_divided_clock_timing(dut):
    clock = Clock(dut.i_Clock, 10, units="ns")  # 100MHz clock (25MHz VGA pixel clock)
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    # Test cycles: 5 VGA horizontal lines * 4 system clocks per VGA clock
    test_cycles = 5 * TOTAL_H * 4
    for cycle in range(test_cycles):
        if cycle % 4000 == 0:
            dut._log.info(f"Progress: {cycle}/{test_cycles} ({100*cycle//test_cycles}%)")

        h_count = int(dut.vga_out.r_H_Counter.value)
        v_count = int(dut.vga_out.r_V_Counter.value)
        clock_count = int(dut.vga_out.r_Clock_Counter.value)

        # Counter bounds checks
        assert 0 <= h_count < TOTAL_H, f"H counter {h_count} out of range"
        assert 0 <= v_count < TOTAL_V, f"V counter {v_count} out of range"
        assert 0 <= clock_count <= 3, f"Clock counter {clock_count} out of range"

        # Horizontal sync timing
        if h_count < VISIBLE_H + FRONT_PORCH_H:
            assert dut.vga_out.o_Horizontal_Sync.value == 1, f"Hsync should be high at H{h_count}"
        elif h_count < VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H:
            assert dut.vga_out.o_Horizontal_Sync.value == 0, f"Hsync should be low at H{h_count}"
        else:
            assert dut.vga_out.o_Horizontal_Sync.value == 1, f"Hsync should be high at H{h_count}"

        # Vertical sync timing
        if v_count < VISIBLE_V + FRONT_PORCH_V:
            assert dut.vga_out.o_Vertical_Sync.value == 1, f"Vsync should be high at V{v_count}"
        elif v_count < VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V:
            assert dut.vga_out.o_Vertical_Sync.value == 0, f"Vsync should be low at V{v_count}"
        else:
            assert dut.vga_out.o_Vertical_Sync.value == 1, f"Vsync should be high at V{v_count}"

        fsync_v_position = VISIBLE_V
        if h_count == 0 and v_count == fsync_v_position:
            assert dut.vga_out.o_mm2s_fsync.value == 1, f"Fsync missing at start of back porch"
        else:
            assert dut.vga_out.o_mm2s_fsync.value == 0, f"Fsync spurious at H{h_count}V{v_count}"

        # VGA counters should only update when clock_count == 3
        if clock_count == 3:
            prev_h = h_count
            prev_v = v_count
            await RisingEdge(dut.i_Clock)
            new_h = int(dut.vga_out.r_H_Counter.value)
            new_v = int(dut.vga_out.r_V_Counter.value)

            # Verify counters incremented correctly
            if prev_h == TOTAL_H - 1:
                assert new_h == 0, f"H counter should wrap: {prev_h} -> {new_h}"
                if prev_v == TOTAL_V - 1:
                    assert new_v == 0, f"V counter should wrap: {prev_v} -> {new_v}"
                else:
                    assert new_v == prev_v + 1, f"V counter should increment: {prev_v} -> {new_v}"
            else:
                assert new_h == prev_h + 1, f"H counter should increment: {prev_h} -> {new_h}"
                assert new_v == prev_v, f"V counter should stay same: {prev_v} -> {new_v}"
        else:
            await RisingEdge(dut.i_Clock)


@cocotb.test()
async def test_vga_simple_vdma(dut):
    clock = Clock(dut.i_Clock, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    white_pixel = pack_rgb(0xF, 0xF, 0xF)
    vdma_task = cocotb.start_soon(drive_vdma_stream(dut, lambda x, y: white_pixel, rows=4, cols=VISIBLE_H))

    # Wait for the first visible pixel of the frame
    while True:
        await wait_pixel_tick(dut)
        if int(dut.vga_out.r_V_Counter.value) == 0 and int(dut.vga_out.r_H_Counter.value) == 0:
            break

    # Check first 32 pixels of the first visible row
    for _ in range(32):
        assert dut.o_Red.value.integer == 0xF
        assert dut.o_Green.value.integer == 0xF
        assert dut.o_Blue.value.integer == 0xF
        await wait_pixel_tick(dut)

    await vdma_task


@cocotb.test()
async def test_vga_pattern_vdma(dut):
    clock = Clock(dut.i_Clock, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    vdma_task = cocotb.start_soon(drive_vdma_stream(dut, pattern_pixel, rows=6, cols=VISIBLE_H))

    # Wait for start of frame
    while True:
        await wait_pixel_tick(dut)
        if int(dut.vga_out.r_V_Counter.value) == 0 and int(dut.vga_out.r_H_Counter.value) == 0:
            break

    # Check a few rows and columns
    for y in range(3):
        for x in range(16):
            exp_r, exp_g, exp_b = pattern_expected(x, y)
            act_r = dut.o_Red.value.integer
            act_g = dut.o_Green.value.integer
            act_b = dut.o_Blue.value.integer
            assert act_r == exp_r, f"R mismatch at ({x},{y}): got {act_r}, expected {exp_r}"
            assert act_g == exp_g, f"G mismatch at ({x},{y}): got {act_g}, expected {exp_g}"
            assert act_b == exp_b, f"B mismatch at ({x},{y}): got {act_b}, expected {exp_b}"
            await wait_pixel_tick(dut)

        # Skip to next line start
        while int(dut.vga_out.r_H_Counter.value) != 0:
            await wait_pixel_tick(dut)

    await vdma_task


@cocotb.test()
async def test_vga_realistic_vdma(dut):
    clock = Clock(dut.i_Clock, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    def gap_func(x, y):
        # Deterministic small latency based on position
        return (x + y) % 3

    vdma_task = cocotb.start_soon(drive_vdma_stream(dut, pattern_pixel, rows=6, cols=VISIBLE_H, gap_func=gap_func))

    # Wait for start of frame
    while True:
        await wait_pixel_tick(dut)
        if int(dut.vga_out.r_V_Counter.value) == 0 and int(dut.vga_out.r_H_Counter.value) == 0:
            break

    # Check a few pixels across two rows
    for y in range(2):
        for x in range(20):
            exp_r, exp_g, exp_b = pattern_expected(x, y)
            act_r = dut.o_Red.value.integer
            act_g = dut.o_Green.value.integer
            act_b = dut.o_Blue.value.integer
            assert act_r == exp_r, f"R mismatch at ({x},{y}): got {act_r}, expected {exp_r}"
            assert act_g == exp_g, f"G mismatch at ({x},{y}): got {act_g}, expected {exp_g}"
            assert act_b == exp_b, f"B mismatch at ({x},{y}): got {act_b}, expected {exp_b}"
            await wait_pixel_tick(dut)

        while int(dut.vga_out.r_H_Counter.value) != 0:
            await wait_pixel_tick(dut)

    await vdma_task


@cocotb.test()
async def test_vga_frame_transition_realistic_vdma(dut):
    """Verify that after a frame boundary the pixel stream restarts at (0,0).

    Uses the same "realistic" deterministic gap pattern as test_vga_realistic_vdma.
    """

    clock = Clock(dut.i_Clock, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    def gap_func(x, y):
        return (x + y) % 3

    # Single progress log line, throttled by wallclock time.
    last_log_wall = time.monotonic()
    phase = "init"

    def log_progress(force=False):
        nonlocal last_log_wall
        now = time.monotonic()
        if (not force) and (now - last_log_wall) < 5.0:
            return
        last_log_wall = now
        dut._log.info(
            f"[frame_transition] phase={phase} sim_ms={get_sim_time(units='ms'):.3f} "
            f"V={int(dut.vga_out.r_V_Counter.value)} H={int(dut.vga_out.r_H_Counter.value)}"
        )

    async def check_first_row(cols_to_check=20):
        for x in range(cols_to_check):
            exp_r, exp_g, exp_b = pattern_expected(x, 0)
            act_r = dut.o_Red.value.integer
            act_g = dut.o_Green.value.integer
            act_b = dut.o_Blue.value.integer
            assert act_r == exp_r, f"R mismatch at ({x},0): got {act_r}, expected {exp_r}"
            assert act_g == exp_g, f"G mismatch at ({x},0): got {act_g}, expected {exp_g}"
            assert act_b == exp_b, f"B mismatch at ({x},0): got {act_b}, expected {exp_b}"
            await wait_pixel_tick(dut)

    # Frame 1: drive just enough data to make row0 valid (use realistic gaps).
    vdma_frame1 = cocotb.start_soon(
        drive_vdma_stream(dut, pattern_pixel, rows=2, cols=VISIBLE_H, gap_func=gap_func)
    )

    # Frame 1 visible start
    phase = "wait_frame1_visible"
    log_progress(force=True)
    while True:
        await wait_pixel_tick(dut)
        log_progress()
        if int(dut.vga_out.r_V_Counter.value) == 0 and int(dut.vga_out.r_H_Counter.value) == 0:
            break

    phase = "check_frame1_row0"
    log_progress(force=True)
    await check_first_row(cols_to_check=20)

    await vdma_frame1
    dut.s_axis_tvalid.value = 0

    # Fast-forward to a clean fsync event without an active VDMA task.
    # Place the DUT exactly at the fsync coordinate and ensure a pixel-tick edge occurs
    # so the RTL executes its per-frame reset (w_Frame_Sync_Event).
    phase = "force_fsync_event"
    log_progress(force=True)
    dut.vga_out.r_V_Counter.value = VISIBLE_V
    dut.vga_out.r_H_Counter.value = 0
    dut.vga_out.r_Clock_Counter.value = 3
    await RisingEdge(dut.i_Clock)

    # Advance one more pixel tick so fsync level deasserts (H becomes 1) and prefetch can run.
    dut.vga_out.r_Clock_Counter.value = 3
    await RisingEdge(dut.i_Clock)

    # Frame 2: start stream at (0,0) immediately after the forced fsync event.
    # The DUT will prefetch one row during vertical blanking.
    phase = "drive_frame2_prefetch"
    log_progress(force=True)
    vdma_frame2 = cocotb.start_soon(
        drive_vdma_stream(
            dut,
            pattern_pixel,
            rows=1,
            cols=VISIBLE_H,
            gap_func=gap_func,
            wait_for_fsync_pulse=False,
        )
    )

    phase = "wait_blank_prefetch_done"
    log_progress(force=True)
    while int(dut.vga_out.r_Blanking_Prefetch_Done.value) == 0:
        await RisingEdge(dut.i_Clock)
        log_progress()

    await vdma_frame2
    dut.s_axis_tvalid.value = 0

    # Now fast-forward to the end of the frame so the next pixel tick wraps to V=0,H=0.
    phase = "fast_forward_to_frame2_start"
    log_progress(force=True)
    dut.vga_out.r_V_Counter.value = TOTAL_V - 1
    dut.vga_out.r_H_Counter.value = TOTAL_H - 1
    dut.vga_out.r_Clock_Counter.value = 3
    await RisingEdge(dut.i_Clock)

    # Frame 2 visible start
    phase = "wait_frame2_visible"
    log_progress(force=True)
    while True:
        await wait_pixel_tick(dut)
        log_progress()
        if int(dut.vga_out.r_V_Counter.value) == 0 and int(dut.vga_out.r_H_Counter.value) == 0:
            break

    phase = "check_frame2_row0"
    log_progress(force=True)
    await check_first_row(cols_to_check=20)

    phase = "done"
    log_progress(force=True)
