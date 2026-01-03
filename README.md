# RISC-V FPGA Computer

Building a computer system from scratch on an FPGA, for fun. Features a custom RISC-V RV32I soft-core CPU, VGA video output, and game peripherals.

## What's This?

A minimal computer system targeting the Arty S7-50 FPGA:
- Custom RISC-V RV32I CPU core (no multiply/divide, no floating point)
- VGA video output (640x480)
- DDR3 memory interface
- Game-focused peripherals (TBD)

This is a learning project to understand computer architecture from the ground up.

## Current Status

**Working on**: DDR3 memory controller initialization

- CPU core: Implemented and passing tests
- Testing: 14 unit tests + 40+ integration tests passing
- Video: VGA module done, framebuffer designed
- Memory: Blocked on MIG (Memory Interface Generator) integration

## Development Approach

The core CPU is written manually in Verilog, for the love of the game.

**Stack:**
- Hardware: Verilog (hand-written, no HLS)
- Testing: Verilator + cocotb (Python)
- Tooling: Go (debugger, utilities)

While auxiliary tools like the debugger are coded with AI assistance, the CPU itself is crafted by hand to deeply understand how processors work.

**Testing:** Good test coverage prevents regression. Manual testing on FPGA takes too long, so automated tests are a necessity. Tests are written in Python using cocotb and simulated with Verilator. Unit tests verify individual modules, integration tests verify full instruction execution.

**Debug Tools:** A UART-based debugger (`tools/debugger/`) allows real-time inspection of the CPU on FPGA - halt/resume, read/write registers and memory, step through instructions. See [docs/ai/debug-protocol.md](docs/ai/debug-protocol.md).

## Repository Contents

- `hdl/` - Verilog source files (CPU, video, peripherals)
- `tests/` - Verilator + cocotb tests
- `tools/` - Debug utilities and toolchain
- `docs/` - Architecture docs and guides
- `config/` - FPGA constraints

## Running Tests

Test dependencies: Verilator, Python 3, cocotb

```bash
cd tests
make              # Run all tests
make cpu          # CPU tests only
make clean        # Clean build artifacts
```

## Documentation

- [docs/everyone/](docs/everyone/) - Setup guides and getting started
- [docs/ai/](docs/ai/) - Detailed architecture and protocol specs
- [CLAUDE.md](CLAUDE.md) - Project context and AI instructions

See [docs/everyone/architecture.md](docs/everyone/architecture.md) for CPU details, memory map, and video system design.
