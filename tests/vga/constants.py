# VGA 640x480@60Hz timing constants (match vga_out.v localparam values)
# Horizontal timing
VISIBLE_H = 640
FRONT_PORCH_H = 16
SYNC_PULSE_H = 96
BACK_PORCH_H = 48
TOTAL_H = 800  # VISIBLE_H + FRONT_PORCH_H + SYNC_PULSE_H + BACK_PORCH_H

# Vertical timing
VISIBLE_V = 480
FRONT_PORCH_V = 10
SYNC_PULSE_V = 2
BACK_PORCH_V = 33
TOTAL_V = 525  # VISIBLE_V + FRONT_PORCH_V + SYNC_PULSE_V + BACK_PORCH_V

# Useful for frame calculations
CLOCKS_PER_FRAME = TOTAL_H * TOTAL_V  # 420,000 clocks per frame