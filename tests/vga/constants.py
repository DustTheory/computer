# VGA 640x480 @ 60Hz timing constants
# These match the values in hdl/vga_out/vga_out.v

# Horizontal timing (in pixels)
VISIBLE_H = 640
FRONT_PORCH_H = 16
SYNC_PULSE_H = 96
BACK_PORCH_H = 48
TOTAL_H = 800  # VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H + BACK_PORCH_H

# Vertical timing (in lines)
VISIBLE_V = 480
FRONT_PORCH_V = 10
SYNC_PULSE_V = 2
BACK_PORCH_V = 33
TOTAL_V = 525  # VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V + BACK_PORCH_V

# Clock divider - module advances pixel counter every 4 clocks
CLOCKS_PER_PIXEL = 4

# Derived timing constants (in clock cycles)
CLOCKS_PER_LINE = TOTAL_H * CLOCKS_PER_PIXEL  # 3200 clocks
CLOCKS_PER_FRAME = TOTAL_V * CLOCKS_PER_LINE  # 1,680,000 clocks

# Horizontal region boundaries (pixel positions)
H_VISIBLE_END = VISIBLE_H                          # 640
H_FRONT_PORCH_END = H_VISIBLE_END + FRONT_PORCH_H  # 656
H_SYNC_END = H_FRONT_PORCH_END + SYNC_PULSE_H      # 752
# H_BACK_PORCH_END = TOTAL_H = 800

# Vertical region boundaries (line positions)
V_VISIBLE_END = VISIBLE_V                          # 480
V_FRONT_PORCH_END = V_VISIBLE_END + FRONT_PORCH_V  # 490
V_SYNC_END = V_FRONT_PORCH_END + SYNC_PULSE_V      # 492
# V_BACK_PORCH_END = TOTAL_V = 525


def make_pixel(r, g, b):
    """Create a 16-bit pixel value from 4-bit RGB components.

    Format: [15:12]=R, [10:7]=G, [4:1]=B (bits 11, 6, 5, 0 unused)
    """
    return ((r & 0xF) << 12) | ((g & 0xF) << 7) | ((b & 0xF) << 1)


# Test color constants
PIXEL_RED = make_pixel(0xF, 0x0, 0x0)
PIXEL_GREEN = make_pixel(0x0, 0xF, 0x0)
PIXEL_BLUE = make_pixel(0x0, 0x0, 0xF)
PIXEL_WHITE = make_pixel(0xF, 0xF, 0xF)
PIXEL_BLACK = make_pixel(0x0, 0x0, 0x0)
PIXEL_TEST = make_pixel(0xA, 0x5, 0x3)  # Arbitrary test pattern
