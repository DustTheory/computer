# Architecture Overview

## CPU Core (RV32I)

- 32-bit RISC-V base integer instruction set (RV32I)
- No M/F/D extensions (no multiply/divide/float)
- 3-stage pipeline: Fetch/Decode/Execute → Memory/Wait → Writeback
- No hazard detection — insert NOPs manually between dependent instructions
- Two AXI4-Lite masters: instruction fetch (read-only) and data load/store

## Memory Map

```
0x80000000 - 0x80000FFF: Boot ROM (4KB BRAM, internal to CPU)
0x80001000 - 0x87F1DFFF: General RAM (~127MB DDR3 via MIG)
0x87F1E000 - 0x87F8EFFF: Framebuffer 0 (614,400 bytes, 640x480x16bpp)
0x87F8F000 - 0x87FFFFFF: Framebuffer 1
0x88000000 - 0x8800FFFF: VDMA Control Registers (AXI-Lite)
```

- CPU_BASE_ADDR: 0x80000000 (PC starts here on reset)
- ROM_BOUNDARY_ADDR: 0x80000FFF (last ROM address)
- RAM_START_ADDR: 0x80001000 (first DDR3 address)

## Video System

- VGA output: 640x480 @ 60Hz, 16-bit pixels (R[15:12], G[10:7], B[4:1])
- VDMA (AXI VDMA v6.3) reads framebuffer from DDR3, streams to vga_out module
- vga_out runs at 100 MHz with ÷4 divider for 25 MHz pixel clock
- External fsync from vga_out → VDMA synchronizes frame reads
- 2 frame store addresses configured (both pointing to same buffer for single-buffered mode)

### VDMA Register Map (base 0x88000000)

| Offset | Register | Notes |
|--------|----------|-------|
| 0x00 | MM2S_VDMACR | RS=bit0, Circular=bit1 |
| 0x04 | MM2S_VDMASR | Halted=bit0 |
| 0x50 | MM2S_VSIZE | Write last — triggers DMA |
| 0x54 | MM2S_HSIZE | Horizontal size in bytes |
| 0x58 | MM2S_FRMDLY_STRIDE | Stride in bytes [15:0] |
| 0x5C | MM2S_SA1 | Frame 1 start address |
| 0x60 | MM2S_SA2 | Frame 2 start address |

## Clock Domains

- **ui_clk (81.25 MHz)**: CPU, SmartConnect, MIG AXI interface, VDMA AXI master
- **CLK_100 (100 MHz)**: VDMA AXI-Stream output, axis_dwidth_converter, vga_out
- **CLK_200 (200 MHz)**: MIG IDELAYCTRL reference clock (mandatory for DDR3 calibration)

Resets: `ui_clk_sync_rst` (active-high, from MIG) drives CPU reset directly. Inverted via NOT gate (`util_vector_logic_1`) to produce active-low `aresetn` for SmartConnect, MIG AXI slave, and VDMA. `vga_out/i_Reset` tied to constant-0 (runs freely after bitstream load).

## Debug Interface

- Protocol: 115200 baud, 8N1, single-byte opcodes
- Commands: halt, resume, reset, ping, read PC, dump pipeline state
- Tool: `tools/debugger/` (Go CLI), `tools/probe.py` (Python periodic monitor)
- See `.claude/rules/debug/debug.md` for full command set
