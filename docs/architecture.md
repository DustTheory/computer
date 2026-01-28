# Architecture Overview

This document provides a high-level overview of the system architecture.

## CPU Core (RV32I)

The CPU is a custom RISC-V implementation:

- 32-bit RISC-V base integer instruction set (RV32I)
- No multiplication/division (no M extension)
- No floating point (no F/D extensions)
- Harvard architecture with separate instruction/data paths
- Pipeline stages: Fetch → Decode → Execute → Memory → Writeback

For detailed CPU internals, see [../ai/cpu-architecture.md](../ai/cpu-architecture.md).

## Memory Map

```
0x80000000 - 0x80000FFF: Boot ROM (4KB BRAM, internal to CPU)
0x80001000 - 0x87F1DFFF: General RAM (~127MB DDR3 via MIG)
0x87F1E000 - 0x87F8EFFF: Framebuffer 0 (462,848 bytes, 640x480x16bpp)
0x87F8F000 - 0x87FFFFFF: Framebuffer 1 (462,848 bytes, 640x480x16bpp)
0x88000000 - 0x8800FFFF: VDMA Control Registers (64KB)
```

Key addresses:
- CPU_BASE_ADDR: 0x80000000 (PC starts here on reset)
- ROM_BOUNDARY_ADDR: 0x80000FFF (last ROM address)
- RAM_START_ADDR: 0x80001000 (first DDR3 address)
- VDMA_CTRL_ADDR: 0x88000000 (VDMA configuration registers)
- Framebuffers are 4K-aligned for DMA compatibility

See [../ai/memory-map.md](../ai/memory-map.md) for detailed memory layout.

## Video System

- VGA output: 640x480 @ 60Hz
- Dual framebuffer for tear-free rendering
- Pixel format: 16-bit (stored), 12-bit RGB output (4 bits per channel)
- VDMA reads framebuffer from DDR3, streams to VGA output module

The video system uses double buffering to prevent tearing. While one framebuffer is being displayed, the CPU can write to the other. Buffer swapping is controlled via VDMA registers.

### VDMA Configuration

- Control registers at 0x88000000 (64KB range)
- MM2S (Memory-Map to Stream) channel only - read from DDR3, output to VGA
- 2 framebuffer addresses configured for double buffering
- External fsync from vga_out module synchronizes frame reads

### Clock Domains

- **ui_clk (81.25 MHz)**: CPU, SmartConnect, MIG AXI interface, VDMA AXI interfaces
- **CLK_100 (100 MHz)**: VGA output module, VDMA AXI-Stream output

**Known issue (TODO)**: proc_sys_reset_0 is clocked by CLK_100 but generates resets for ui_clk domain components (SmartConnect, MIG, VDMA). This works in practice but is not clean. Should add a second proc_sys_reset on ui_clk for proper reset synchronization.

## Debug Interface

The system includes a UART-based debug peripheral for development:

- Protocol: 115200 baud, 8N1
- Commands: halt, resume, reset, read/write registers, read/write memory
- See [../ai/debug-protocol.md](../ai/debug-protocol.md) for protocol details

Debug tool is in `tools/debugger/` (written in Go).

## System Block Diagram

```
┌─────────────────────────────────────────────────────┐
│                    Top Level (gpu.v)                 │
│                                                       │
│  ┌──────────┐         ┌──────────────┐              │
│  │ CPU Core │────────▶│ Memory       │              │
│  │ (RV32I)  │         │ Interface    │              │
│  └──────────┘         │ (MIG DDR3)   │              │
│       │               └──────────────┘              │
│       │                                              │
│       ├──────────────▶ Framebuffer ──────┐          │
│       │                                   │          │
│       └──────────────▶ Debug Peripheral  │          │
│                                           ▼          │
│                                    ┌──────────┐     │
│                                    │ VGA Out  │────▶ Monitor
│                                    └──────────┘     │
└─────────────────────────────────────────────────────┘
```

## Development Roadmap

Current focus is on getting the system booting and running basic programs:

1. **DDR3 Memory** (current) - Get MIG working for CPU memory access
2. **Boot ROM** - Simple boot code to initialize system
3. **Framebuffer Integration** - Connect video output to DDR3-backed buffer
4. **Peripherals** - Add game-specific I/O (buttons, audio, etc.)

Once the basic system is working, the focus will shift to writing programs and games for it.