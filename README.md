# RISC-V FPGA Computer

[![Tests](https://github.com/DustTheory/computer/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/DustTheory/computer/actions/workflows/test-coverage.yml)

Building a computer system from scratch on an FPGA, for fun. Features a custom RISC-V RV32I soft-core CPU, VGA video output, and game peripherals.

## What's This?

A minimal computer system targeting the Arty S7-50 FPGA:
- Custom RISC-V RV32I CPU core (no multiply/divide, no floating point)
- VGA video output (640x480)
- DDR3 memory interface
- Game-focused peripherals (TBD)

This is a learning project to understand computer architecture from the ground up.

## Current Status

- CPU core: RV32I implemented and passing tests
- Memory: DDR3 operational @ 81.25 MHz
- Testing: unit + integration tests passing
- Video: VGA works — DDR3-backed framebuffer via VDMA, 640x480@60Hz
- Debug: UART debug peripheral works (`tools/debugger/`)

## Development Approach

**Stack:**
- Hardware: Verilog (hand-written, no HLS)
- Testing: Verilator + cocotb (Python)
- Tooling: Go (debugger, utilities)

While auxiliary tools like the debugger are coded with AI assistance, the CPU itself is crafted by hand to deeply understand how processors work.

**Testing:** Good test coverage prevents regression. Manual testing on FPGA takes too long, so automated tests are a necessity. Tests are written in Python using cocotb and simulated with Verilator. There are separate unit and integration tests.

**Debug Tools:** A UART-based debugger (`tools/debugger/`) allows real-time inspection of the CPU on FPGA - halt/resume, read/write registers, jump through code, get extra debug information.

## Repository Contents

- `hdl/` - Verilog source files (CPU, video, peripherals)
- `tests/` - Verilator + cocotb tests
- `tools/` - Debug utilities and toolchain
- `docs/` - Architecture docs and guides
- `config/` - FPGA constraints
- `build.tcl` - the build script

## Running Tests

Test dependencies: Verilator, Python 3, cocotb

```bash
cd tests
source test_env/bin/activate
make TEST_TYPE=unit         # Run unit tests
make TEST_TYPE=integration  # Run integration tests
make TEST_TYPE=all          # Run all tests
```

## Documentation

- [docs/getting-started.md](docs/getting-started.md) - Setup and getting started
- [docs/architecture.md](docs/architecture.md) - CPU details, memory map, and system design
- [CLAUDE.md](CLAUDE.md) - Project context for AI assistants
