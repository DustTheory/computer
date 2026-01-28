# GPU FPGA Project

Minimal computer on Arty S7-50: RV32I CPU + VGA + UART debug.

## Commands

```bash
# Run tests (must activate venv first)
cd tests && source test_env/bin/activate && make

# Test types: unit, integration, vga, all
make TEST_TYPE=unit
make TEST_TYPE=integration
make TEST_TYPE=vga
make TEST_TYPE=all

# Single test file
make TEST_TYPE=integration TEST_FILE=test_add_instruction

# Debug tool
cd tools && go run ./debugger
```

## Memory Map

```
0x80000000 - 0x80000FFF: Boot ROM (4KB BRAM)
0x80001000 - 0x87F1DFFF: RAM (~127MB DDR3)
0x87F1E000 - 0x87F8EFFF: Framebuffer 0 (640x480x12bpp)
0x87F8F000 - 0x87FFFFFF: Framebuffer 1 (640x480x12bpp)
```

- PC starts at 0x80000000 on reset
- ROM_BOUNDARY_ADDR = 0x80000FFF
- Framebuffers are 4K-aligned for DMA

## Constraints

- CPU runs at 81.25 MHz (MIG ui_clk)
- UART: 115200 baud, 706 clocks/bit
- 3-stage pipeline, no hazard detection - insert NOPs between dependent instructions
- DDR3 requires 200 MHz ref_clk, Bank 34 only (1.35V)

## Gotchas

- Tests fail with import errors if venv not activated
- CPU reset must use MIG's `ui_clk_sync_rst`, NOT `peripheral_reset`
- No alignment checks - misaligned loads/stores behave unexpectedly
- Constants in `.vh` files must stay in sync with `tests/cpu/constants.py`
- Vivado project not in repo - recreate from `config/arty-s7-50.xdc`
