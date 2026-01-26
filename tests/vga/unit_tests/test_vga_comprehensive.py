import cocotb
from cocotb.triggers import RisingEdge
from cocotb.clock import Clock
from vga.constants import *

async def simple_vdma_simulator(dut):
    """Simple VDMA that sends white pixels whenever tready is high"""
    white_pixel = 0xF79E  # White: R=15, G=15, B=15 (bits 15:12, 10:7, 4:1)

    while True:
        if dut.vga_out.s_axis_tready.value:
            dut.s_axis_tdata.value = white_pixel
            dut.s_axis_tvalid.value = 1
        else:
            dut.s_axis_tvalid.value = 0

        await RisingEdge(dut.i_Clock)

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
async def test_vga_with_simple_vdma(dut):
    clock = Clock(dut.i_Clock, 10, units="ns")  # 100MHz clock (25MHz VGA pixel clock)
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0

    for _ in range(10):
        await RisingEdge(dut.i_Clock)

    dut.i_Reset.value = 0
    await RisingEdge(dut.i_Clock)

    # Start VDMA simulator in background
    cocotb.start_soon(simple_vdma_simulator(dut))

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

        # RGB validation - white pixel 0xF79E decodes to Red=15, Green=15, Blue=15
        if h_count < VISIBLE_H and v_count < VISIBLE_V:
            expected_red = 15
            expected_green = 15  # 0xF79E bits [10:7] = 0xF
            expected_blue = 15   # 0xF79E bits [4:1] = 0xF

            actual_red = int(dut.vga_out.o_Red.value)
            actual_green = int(dut.vga_out.o_Green.value)
            actual_blue = int(dut.vga_out.o_Blue.value)

            assert actual_red == expected_red, f"Red mismatch at H{h_count}V{v_count}: expected {expected_red}, got {actual_red}"
            assert actual_green == expected_green, f"Green mismatch at H{h_count}V{v_count}: expected {expected_green}, got {actual_green}"
            assert actual_blue == expected_blue, f"Blue mismatch at H{h_count}V{v_count}: expected {expected_blue}, got {actual_blue}"
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