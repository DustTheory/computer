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
0x00000000 - 0x00000FFF: Boot ROM (4KB)
0x10000000 - 0x1FFFFFFF: DDR3 RAM (via MIG, 256MB planned)
0x20000000 - 0x2FFFFFFF: Framebuffer
0x30000000 - 0x3FFFFFFF: Peripherals
0x40000000 - 0x4FFFFFFF: Debug peripheral
```

See [../ai/memory-map.md](../ai/memory-map.md) for detailed memory layout.

## Video System

- VGA output: 640x480 @ 60Hz
- Dual framebuffer for tear-free rendering
- Pixel format: TBD (likely 8-bit indexed color)

The video system uses double buffering to prevent tearing. While one framebuffer is being displayed, the CPU can write to the other. A register controls which buffer is active.

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