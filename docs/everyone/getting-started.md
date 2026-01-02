# Getting Started

This guide will help you set up the test environment and run your first simulation.

## Prerequisites

For testing and simulation, you'll need:

1. **Verilator** (for simulation)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install verilator

   # macOS
   brew install verilator
   ```

2. **Python 3** (for test framework)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip

   # macOS
   brew install python3
   ```

3. **cocotb** (Python test framework)
   ```bash
   pip3 install cocotb pytest
   ```

4. **Go** (for debug tools, optional)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install golang

   # macOS
   brew install go
   ```

## Running Your First Test

1. Clone the repository and navigate to the test directory:
   ```bash
   cd tests
   ```

2. Run the complete test suite:
   ```bash
   make
   ```

   You should see output like:
   ```
   Running CPU unit tests...
   ✓ ALU test passed
   ✓ Register file test passed
   ...
   All tests passed!
   ```

3. Run specific test categories:
   ```bash
   make cpu          # CPU tests only
   make integration  # Integration tests only
   ```

4. Clean build artifacts:
   ```bash
   make clean
   ```

## Understanding Test Output

When tests run, you'll see:

- **PASS**: Test succeeded
- **FAIL**: Test failed (check error messages)

## Project Structure at a Glance

```
hdl/                    # All Verilog source files
├── cpu/                # CPU core modules
├── debug_peripheral/   # Debug interface
└── *.v                # Other system modules

tests/                  # All tests
├── cpu/unit_tests/     # Test individual modules
└── cpu/integration_tests/  # Test full instructions

tools/                  # Utilities
├── debugger/          # UART debug tool
└── compiler/          # Toolchain (TBD)

docs/
├── ai/                # Technical specs
└── everyone/          # This guide
```

## Next Steps

- **To understand the CPU**: See [../ai/cpu-architecture.md](../ai/cpu-architecture.md)
- **To write tests**: See [../ai/test-guide.md](../ai/test-guide.md)
- **To debug hardware**: See [../ai/debug-protocol.md](../ai/debug-protocol.md)
