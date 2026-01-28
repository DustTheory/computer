# ROM Programs for Screen Fill

This directory contains two ROM programs that fill the VGA screen with patterns.

## Programs

### 1. fill_screen.rom - Solid White Screen
**Size**: 84 bytes (21 instructions)

Fills the entire framebuffer (640x480 pixels) with white pixels and configures the VDMA to display it.

**What it does:**
1. Fills all 307,200 pixels (153,600 words) with 0xFFFFFFFF (white)
2. Configures VDMA MM2S registers:
   - Start address: 0x87F1E000 (Framebuffer 0)
   - Horizontal size: 1280 bytes (640 pixels × 2 bytes/pixel)
   - Stride: 1280 bytes
   - Vertical size: 480 lines
   - Control: 0x13 (Run + Circular mode + Frame count enable)
3. Infinite loop

**Expected result**: Solid white screen on VGA output

### 2. fill_pattern.rom - Gradient Pattern
**Size**: 88 bytes (22 instructions)

Fills the framebuffer with a rainbow gradient pattern and configures VDMA.

**What it does:**
1. Fills framebuffer with incrementing pattern (adds 0x111 per word)
   - Creates a horizontal color gradient
   - Pattern wraps around creating colored stripes
2. Configures VDMA (same as above)
3. Infinite loop

**Expected result**: Colorful gradient/striped pattern on VGA output

## Usage

### On the FPGA:

1. Copy the desired `.rom` file to `hdl/cpu/instruction_memory/rom.mem`:
   ```bash
   cp fill_screen.rom hdl/cpu/instruction_memory/rom.mem
   # OR
   cp fill_pattern.rom hdl/cpu/instruction_memory/rom.mem
   ```

2. Rebuild the FPGA bitstream in Vivado

3. Program the FPGA

4. Connect VGA monitor and observe the output

### In Simulation:

If you want to test in Verilator/cocotb:
1. Copy the ROM file to the test directory as `rom.mem`
2. Run the simulation
3. The framebuffer memory should be filled with the pattern

## Memory Map Reference

- **ROM**: 0x80000000 - 0x80000FFF (4KB)
- **RAM**: 0x80001000 - 0x87F1DFFF (~127MB)
- **Framebuffer 0**: 0x87F1E000 - 0x87F8EFFF (614,400 bytes)
- **Framebuffer 1**: 0x87F8F000 - 0x87FFFFFF (614,400 bytes)
- **VDMA Control**: 0x88000000 - 0x8800FFFF (64KB)

## VDMA Register Offsets

The programs configure these MM2S (Memory-Map to Stream) registers:

- **0x00**: MM2S_VDMACR (Control Register)
  - Bit 0: Run/Stop
  - Bit 1: Circular mode
  - Bit 4: Frame count enable
- **0x18**: MM2S_START_ADDRESS (Framebuffer base address)
- **0x20**: MM2S_VSIZE (Vertical size in lines)
- **0x24**: MM2S_HSIZE (Horizontal size in bytes)
- **0x28**: MM2S_STRIDE (Number of bytes between rows)

## Pixel Format

- **Storage**: 16-bit per pixel (RGB565 or similar)
- **Output**: 12-bit RGB (4 bits per channel)
- **Screen resolution**: 640×480 @ 60Hz

## Assembly Source

The assembly source files are provided for reference:
- `fill_screen.s` - Assembly source for white fill
- `assemble.py` - Assembler script for white fill
- `assemble_pattern.py` - Assembler script for pattern fill

To regenerate the ROM files:
```bash
python3 assemble.py          # Generates fill_screen.rom
python3 assemble_pattern.py  # Generates fill_pattern.rom
```

## Troubleshooting

**No display**:
- Check that VDMA is initialized and running
- Verify VGA clock is working (100 MHz for pixel clock)
- Check that DDR3 MIG is calibrated (ui_clk @ 81.25 MHz)

**Corrupt/garbled display**:
- Verify framebuffer addresses are correct
- Check VDMA stride matches horizontal size
- Ensure pixel format matches VGA output expectations

**Blank screen (not black, but no sync)**:
- VGA sync signals may not be working
- Check VGA output module is enabled

## Technical Notes

- These programs run directly from ROM (first 4KB)
- The fill loop takes approximately (153,600 instructions × ~5 cycles) ≈ 768,000 cycles
- At 81.25 MHz, filling takes ~9.4ms
- VDMA reads framebuffer continuously at 60 Hz (16.67ms per frame)
- Programs use only RV32I base instructions (no M/F/D extensions)
