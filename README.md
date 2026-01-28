# RISC-V FPGA Computer

[![Tests](https://github.com/DustTheory/computer/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/DustTheory/computer/actions/workflows/test.yml)

Building a computer system from scratch on an FPGA, for fun. Features a custom RISC-V RV32I soft-core CPU, VGA video output, and game peripherals.

## What's This?

A minimal computer system targeting the Arty S7-50 FPGA:
- Custom RISC-V RV32I CPU core (no multiply/divide, no floating point)
- VGA video output (640x480)
- DDR3 memory interface

This is a learning project to understand computer architecture from the ground up.

## Current Status

- **CPU**: RV32I core with 3-stage pipeline, no caches, no M extension yet
- **Memory**: DDR3 via AXI4-Lite (full AXI4 not implemented yet)
- **Video**: 640x480 VGA with double-buffered framebuffer, VDMA for display
- **Debug**: UART interface enables halting, stepping, register/memory inspection
- **Input**: Not implemented

## Development Approach

The core CPU is written manually in Verilog, for the love of the game.

**Stack:**
- Hardware: Verilog (hand-written, no HLS)
- Testing: Verilator + cocotb (Python)
- Tooling: Go (debugger, utilities)

While auxiliary tools like the debugger are coded with AI assistance, the CPU itself is crafted by hand to deeply understand how processors work.

**Testing:** Good test coverage prevents regression. Manual testing on FPGA takes too long, so automated tests are a necessity. Tests are written in Python using cocotb and simulated with Verilator. Unit tests verify individual modules, integration tests verify full instruction execution.

**Debug Tools:** A UART-based debugger (`tools/debugger/`) allows real-time inspection of the CPU on FPGA - halt/resume, read/write registers and memory, step through instructions.

## Repository Contents

- `hdl/` - Verilog source files (CPU, video, peripherals)
- `tests/` - Verilator + cocotb tests
- `tools/` - Debug utilities and toolchain
- `config/` - FPGA constraints

## Setup

**Dependencies**: Verilator, Python 3, Go

```bash
# Create Python venv and install test dependencies
cd tests
python3 -m venv test_env
source test_env/bin/activate
pip install cocotb pytest
```

## Running Tests

```bash
cd tests
source test_env/bin/activate
make TEST_TYPE=unit         # Run unit tests
make TEST_TYPE=integration  # Run integration tests
make TEST_TYPE=vga          # Run VGA tests
make TEST_TYPE=all          # Run all tests
```
