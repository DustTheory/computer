from cocotb.triggers import ClockCycles, RisingEdge

from vga.constants import CLOCKS_PER_PIXEL, CLOCKS_PER_LINE, TOTAL_H, TOTAL_V


async def wait_pixels(dut, num_pixels):
    """Wait for the specified number of pixel periods."""
    await ClockCycles(dut.i_Clock, num_pixels * CLOCKS_PER_PIXEL)


async def wait_lines(dut, num_lines):
    """Wait for the specified number of complete lines."""
    await ClockCycles(dut.i_Clock, num_lines * CLOCKS_PER_LINE)


async def wait_for_frame_start(dut):
    """Wait until we're at the start of a frame (position near 0,0).

    For tests that need to start from a known position.
    """
    # Wait a couple cycles to let signals settle at simulation start
    await ClockCycles(dut.i_Clock, 2)

    # Check if we're already at or very near frame start (first 10 pixels of line 0)
    h, v = get_current_position(dut)
    if v == 0 and h < 10:
        # Already at frame start, just return
        return True

    # Need to wait for next frame - calculate how many pixels
    pixels_remaining_in_line = TOTAL_H - h
    lines_remaining = TOTAL_V - v - 1  # -1 because current line is partial

    # Total pixels to next frame start
    pixels_to_frame_start = pixels_remaining_in_line + (lines_remaining * TOTAL_H)

    # Jump ahead to frame start
    if pixels_to_frame_start > 5:
        await wait_pixels(dut, pixels_to_frame_start - 2)

    # Poll for exact frame start (when counters roll over to 0,0)
    for _ in range(50):
        await RisingEdge(dut.i_Clock)
        h, v = get_current_position(dut)
        if v == 0 and h < 5:
            return True

    raise TimeoutError("wait_for_frame_start: failed to find frame start")


async def wait_for_hsync_pulse(dut):
    """Wait for horizontal sync to go low (active)."""
    # If already in hsync, wait for it to end first
    while dut.o_Horizontal_Sync.value == 0:
        await RisingEdge(dut.i_Clock)

    # Now wait for next hsync
    for _ in range(TOTAL_H * CLOCKS_PER_PIXEL + 100):
        await RisingEdge(dut.i_Clock)
        if dut.o_Horizontal_Sync.value == 0:
            return True

    raise TimeoutError("wait_for_hsync_pulse timed out")


async def wait_for_vsync_pulse(dut):
    """Wait for vertical sync to go low (active)."""
    # If already in vsync, wait for it to end first
    while dut.o_Vertical_Sync.value == 0:
        await RisingEdge(dut.i_Clock)

    # Now wait for next vsync - could be up to a full frame
    for _ in range(TOTAL_H * TOTAL_V * CLOCKS_PER_PIXEL + 100):
        await RisingEdge(dut.i_Clock)
        if dut.o_Vertical_Sync.value == 0:
            return True

    raise TimeoutError("wait_for_vsync_pulse timed out")


def get_current_position(dut):
    """Get current H and V counter positions from internal registers."""
    h_counter = dut.vga_out.r_H_Counter.value.integer
    v_counter = dut.vga_out.r_V_Counter.value.integer
    return h_counter, v_counter


def extract_rgb(dut):
    """Extract R, G, B values from VGA outputs."""
    r = dut.o_Red.value.integer
    g = dut.o_Green.value.integer
    b = dut.o_Blue.value.integer
    return r, g, b
