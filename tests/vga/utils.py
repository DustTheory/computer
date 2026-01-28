from cocotb.triggers import RisingEdge

from vga.constants import VISIBLE_H, VISIBLE_V


def pack_rgb(red, green, blue):
	"""Pack 4-bit RGB into 16-bit pixel format used by vga_out."""
	return ((red & 0xF) << 12) | ((green & 0xF) << 7) | ((blue & 0xF) << 1)


async def wait_for_fsync(dut):
	"""Wait for mm2s fsync pulse."""
	while True:
		await RisingEdge(dut.i_Clock)
		if dut.o_mm2s_fsync.value.integer == 1:
			return


async def drive_vdma_stream(dut, pixel_func, rows=VISIBLE_V, cols=VISIBLE_H, gap_func=None):
	"""Drive AXI-Stream pixel data honoring tready and optional gaps."""
	await wait_for_fsync(dut)

	x = 0
	y = 0
	gap = 0

	dut.s_axis_tvalid.value = 0
	dut.s_axis_tdata.value = 0

	while y < rows:
		if gap > 0:
			dut.s_axis_tvalid.value = 0
			gap -= 1
			await RisingEdge(dut.i_Clock)
			continue

		dut.s_axis_tdata.value = pixel_func(x, y)
		dut.s_axis_tvalid.value = 1
		await RisingEdge(dut.i_Clock)

		if dut.s_axis_tready.value.integer == 1:
			x += 1
			if x >= cols:
				x = 0
				y += 1
			if gap_func is not None:
				gap = int(gap_func(x, y))

	dut.s_axis_tvalid.value = 0
