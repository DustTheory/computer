import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from vga.constants import *
import os

def calculate_pixel_rgb(row, col):
    """Calculate RGB values based on row and column position"""
    red = col % 16                      # Red varies with column
    green = row % 16                    # Green varies with row
    blue = (col + row) % 16             # Blue varies with both
    return red, green, blue

def save_pixel_data(pixel_list, filename):
    """Save pixel data to text file for easy comparison"""
    os.makedirs("test_output", exist_ok=True)

    with open(f"test_output/{filename}", 'w') as f:
        f.write("# Format: cycle,h_count,v_count,red,green,blue\n")
        for entry in pixel_list:
            cycle, h, v, r, g, b = entry
            f.write(f"{cycle},{h},{v},{r},{g},{b}\n")
    print(f"Saved pixel data: test_output/{filename} ({len(pixel_list)} pixels)")

def save_vdma_data(vdma_list, filename):
    """Save VDMA data to text file for easy comparison"""
    os.makedirs("test_output", exist_ok=True)

    with open(f"test_output/{filename}", 'w') as f:
        f.write("# Format: cycle,row,col,pixel_data_hex,red,green,blue,blanking_prefetch_done,fill_addr,active_buffer,tready\n")
        for entry in vdma_list:
            if len(entry) == 7:
                # Legacy format without diagnostics
                cycle, row, col, pixel_data, r, g, b = entry
                f.write(f"{cycle},{row},{col},{pixel_data:04X},{r},{g},{b},,,\n")
            else:
                # New format with diagnostics
                cycle, row, col, pixel_data, r, g, b, blanking_prefetch_done, fill_addr, active_buffer, tready = entry
                f.write(f"{cycle},{row},{col},{pixel_data:04X},{r},{g},{b},{blanking_prefetch_done},{fill_addr},{active_buffer},{tready}\n")
    print(f"Saved VDMA data: test_output/{filename} ({len(vdma_list)} pixels)")

async def pattern_vdma_simulator(dut, capture_data=None):
    """VDMA that maintains its own counters and uses frame sync for synchronization"""
    current_row = 0
    current_col = 0
    prev_fsync = 0
    cycle = 0

    while True:
        # Check for frame sync rising edge to reset position
        fsync = int(dut.vga_out.o_mm2s_fsync.value)
        if fsync and not prev_fsync:
            current_row = 0
            current_col = 0
        prev_fsync = fsync

        # Always provide data when we have it (proactive DMA)
        if current_row < VISIBLE_V:
            # Generate RGB based on VDMA's own position counters using shared formula
            red, green, blue = calculate_pixel_rgb(current_row, current_col)

            # Pack into 16-bit pixel: Red[15:12], Green[10:7], Blue[4:1]
            pixel_data = (red << 12) | (green << 7) | (blue << 1)

            dut.s_axis_tdata.value = pixel_data
            dut.s_axis_tvalid.value = 1

            # Capture VDMA data when requested and handshake occurs
            if capture_data is not None and dut.vga_out.s_axis_tready.value:
                # Get diagnostic signals for debugging buffer management
                blanking_prefetch_done = int(dut.vga_out.r_Blanking_Prefetch_Done.value)
                fill_addr = int(dut.vga_out.r_Fill_Addr.value)
                active_buffer = int(dut.vga_out.r_Active_Buffer.value)
                tready = int(dut.vga_out.s_axis_tready.value)

                capture_data.append((cycle, current_row, current_col, pixel_data, red, green, blue,
                                   blanking_prefetch_done, fill_addr, active_buffer, tready))

            # Advance VDMA's position counters only when handshake completes
            if dut.vga_out.s_axis_tready.value:
                current_col += 1
                if current_col >= VISIBLE_H:
                    current_col = 0
                    current_row += 1
        else:
            dut.s_axis_tvalid.value = 0

        cycle += 1
        await RisingEdge(dut.i_Clock)

@cocotb.test()
async def test_vga_with_pattern_vdma(dut):
    clock = Clock(dut.i_Clock, 10, units="ns")  # 100MHz clock (25MHz VGA pixel clock)
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    # Start pattern VDMA simulator in background
    cocotb.start_soon(pattern_vdma_simulator(dut))

    # Test cycles: 10 VGA horizontal lines * 4 system clocks per VGA clock (same as other tests)
    test_cycles = 10 * TOTAL_H * 4
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

        # Removed verbose VDMA logging and debug logs

        # RGB pattern validation - Simple validation for 10 lines
        if h_count < VISIBLE_H and v_count < VISIBLE_V:
            actual_red = int(dut.vga_out.o_Red.value)
            actual_green = int(dut.vga_out.o_Green.value)
            actual_blue = int(dut.vga_out.o_Blue.value)

            # Calculate expected RGB values for this exact position
            exp_red, exp_green, exp_blue = calculate_pixel_rgb(v_count, h_count)

    
            assert actual_red == exp_red, f"Red mismatch at H{h_count}V{v_count}: expected {exp_red}, got {actual_red}"
            assert actual_green == exp_green, f"Green mismatch at H{h_count}V{v_count}: expected {exp_green}, got {actual_green}"
            assert actual_blue == exp_blue, f"Blue mismatch at H{h_count}V{v_count}: expected {exp_blue}, got {actual_blue}"
        elif h_count >= VISIBLE_H or v_count >= VISIBLE_V:
            # RGB should be black during blanking
            assert int(dut.vga_out.o_Red.value) == 0, f"Red not black during blanking at H{h_count}V{v_count}"
            assert int(dut.vga_out.o_Green.value) == 0, f"Green not black during blanking at H{h_count}V{v_count}"
            assert int(dut.vga_out.o_Blue.value) == 0, f"Blue not black during blanking at H{h_count}V{v_count}"

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
async def test_vga_frame_transition(dut):
    """Test VGA frame transitions to ensure timing improvements work across frame boundaries"""
    clock = Clock(dut.i_Clock, 10, units="ns")  # 100MHz clock (25MHz VGA pixel clock)
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    # Create data capture lists
    vga_output_data = []
    vdma_input_data = []

    # Start pattern VDMA simulator in background with data capture
    cocotb.start_soon(pattern_vdma_simulator(dut, vdma_input_data))

    # Test cycles: Cover frame transition - ~75 lines to see frame boundary
    transition_lines = 75
    test_cycles = transition_lines * TOTAL_H * 4

    try:
        for cycle in range(test_cycles):
            if cycle % 50000 == 0:
                dut._log.info(f"Frame transition test progress: {cycle}/{test_cycles} ({100*cycle//test_cycles}%)")

            h_count = int(dut.vga_out.r_H_Counter.value)
            v_count = int(dut.vga_out.r_V_Counter.value)
            clock_count = int(dut.vga_out.r_Clock_Counter.value)

            # Log key timing events
            if h_count == 0 and clock_count == 0:
                fsync_v_pos = VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V + (BACK_PORCH_V >> 1)  # INITIAL_V_COUNT
                if v_count == fsync_v_pos:
                    dut._log.info(f"🔄 Frame sync at V={v_count} - VDMA resetting for next frame")
                elif v_count == 0:
                    dut._log.info("🎯 Frame 2 visible area starts - testing improved VGA timing!")
                elif v_count < 5:  # Debug first few rows
                    dut._log.info(f"📍 Early visible row V={v_count}")

            # Debug pixel mismatch at the specific failing positions
            if (h_count <= 1 and v_count == 3) or (h_count == 0 and v_count <= 4):
                actual_red = int(dut.vga_out.o_Red.value)
                actual_green = int(dut.vga_out.o_Green.value)
                actual_blue = int(dut.vga_out.o_Blue.value)
                exp_red, exp_green, exp_blue = calculate_pixel_rgb(v_count, h_count)
                dut._log.info(f"🔍 H{h_count}V{v_count} debug: actual RGB=({actual_red},{actual_green},{actual_blue}) expected=({exp_red},{exp_green},{exp_blue})")
                dut._log.info(f"    Buffer state: active={int(dut.vga_out.r_Active_Buffer.value)}, fill_addr={int(dut.vga_out.r_Fill_Addr.value)}")
                dut._log.info(f"    VDMA: tready={int(dut.vga_out.s_axis_tready.value)}, tvalid={int(dut.s_axis_tvalid.value)}, tdata=0x{int(dut.s_axis_tdata.value):04X}")
                dut._log.info(f"    Frame sync: {int(dut.vga_out.o_mm2s_fsync.value)}")

            # Validate visible pixels
            if h_count < VISIBLE_H and v_count < VISIBLE_V:
                actual_red = int(dut.vga_out.o_Red.value)
                actual_green = int(dut.vga_out.o_Green.value)
                actual_blue = int(dut.vga_out.o_Blue.value)

                # Capture VGA output data
                vga_output_data.append((cycle, h_count, v_count, actual_red, actual_green, actual_blue))

                exp_red, exp_green, exp_blue = calculate_pixel_rgb(v_count, h_count)

                # Skip assertions on first 2 rows to collect more data
                # if v_count >= 2:
                assert actual_red == exp_red, f"Red mismatch at H{h_count}V{v_count}: expected {exp_red}, got {actual_red}"
                assert actual_green == exp_green, f"Green mismatch at H{h_count}V{v_count}: expected {exp_green}, got {actual_green}"
                assert actual_blue == exp_blue, f"Blue mismatch at H{h_count}V{v_count}: expected {exp_blue}, got {actual_blue}"

            elif h_count >= VISIBLE_H or v_count >= VISIBLE_V:
                # RGB should be black during blanking
                assert int(dut.vga_out.o_Red.value) == 0, f"Red not black during blanking at H{h_count}V{v_count}"
                assert int(dut.vga_out.o_Green.value) == 0, f"Green not black during blanking at H{h_count}V{v_count}"
                assert int(dut.vga_out.o_Blue.value) == 0, f"Blue not black during blanking at H{h_count}V{v_count}"

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

    finally:
        # Save captured data to files for comparison, even if test fails
        save_pixel_data(vga_output_data, "vga_output_data.txt")
        save_vdma_data(vdma_input_data, "vdma_input_data.txt")

        dut._log.info(f"Test completed. Captured {len(vga_output_data)} VGA pixels and {len(vdma_input_data)} VDMA pixels")