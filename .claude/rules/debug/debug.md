---
paths:
  - hdl/debug_peripheral/**
  - tools/debugger/**
---

# Debug Protocol

**Last updated**: 2026-01-05
**Sources**: [debug_peripheral.v](hdl/debug_peripheral/debug_peripheral.v), [debug_peripheral.vh](hdl/debug_peripheral/debug_peripheral.vh)

UART debug peripheral for CPU control via serial commands (115200 baud, 8N1).

## Overview

**Module**: [debug_peripheral.v](hdl/debug_peripheral/debug_peripheral.v)

**Ports**:
- `i_Uart_Tx_In` - UART RX from host (host → FPGA)
- `o_Uart_Rx_Out` - UART TX to host (FPGA → host)
- `o_Halt_Cpu` - Stops CPU when high
- `o_Reset_Cpu` - Holds CPU in reset when high
- `i_PC[31:0]` - Program counter (for READ_PC command)

## Command Set

Single-byte opcodes:

| Opcode | Command | Action | Response |
|--------|---------|--------|----------|
| `0x00` | NOP | No operation | None |
| `0x01` | RESET | Assert CPU reset | None |
| `0x02` | UNRESET | Deassert CPU reset | None |
| `0x03` | HALT | Halt CPU | None |
| `0x04` | UNHALT | Resume CPU | None |
| `0x05` | PING | Test connectivity | `0xAA` |
| `0x06` | READ_PC | Read program counter | 4 bytes (little-endian) |
| `0x07` | WRITE_PC | Write PC (stub) | None |
| `0x08` | READ_REGISTER | Read register (stub) | TBD |
| `0x09` | WRITE_REGISTER | Write register (stub) | TBD |

**Implemented**: NOP, RESET, UNRESET, HALT, UNHALT, PING, READ_PC
**Stubs**: WRITE_PC, READ_REGISTER, WRITE_REGISTER (opcodes defined, logic incomplete)

## State Machine

**States**: `IDLE` → `DECODE_AND_EXECUTE` → `IDLE`

**Flow**:
1. IDLE: Wait for UART byte
2. DECODE_AND_EXECUTE: Execute opcode, queue response (if any), return to IDLE

**Output buffer**: 256-byte FIFO for responses (PING → `0xAA`, READ_PC → 4 bytes, etc.)

## UART Timing

**Baud rate**: 115200 bps
**CPU clock**: 81.25 MHz (MIG ui_clk)
**Clocks per bit**: 81,250,000 / 115,200 ≈ **706 clocks**

**Modules**: [uart_receiver.v](hdl/debug_peripheral/uart_receiver.v), [uart_transmitter.v](hdl/debug_peripheral/uart_transmitter.v)

**Interface**:
- RX: `o_Rx_DV` pulses for 1 cycle when byte received, `o_Rx_Byte` contains data
- TX: Assert `i_Tx_DV` for 1 cycle with `i_Tx_Byte`, wait for `o_Tx_Done` pulse

## Go Debugger Tool

**Location**: [tools/debugger/](tools/debugger/)
**Run**: `go run tools/debugger/main.go`

**Status**:
- ✓ Halt, Unhalt, Reset, Unreset, Ping implemented in Go tool
- ✗ Read PC, Write PC, Read/Write Register not yet in tool
- ✓ All basic commands work on FPGA (PING returns `0xAA`)

**Opcode constants**: See [opcodes.go](tools/debugger/opcodes.go) - must match [debug_peripheral.vh](hdl/debug_peripheral/debug_peripheral.vh)

## Testing

**Integration tests**: See [tests/cpu/integration_tests/](tests/cpu/integration_tests/)
- [test_debug_ping.py](tests/cpu/integration_tests/test_debug_ping.py) - PING command verification
- [test_debug_read_pc.py](tests/cpu/integration_tests/test_debug_read_pc.py) - READ_PC command verification

**Test pattern**:
```python
from cpu.utils import uart_send_byte, uart_wait_for_byte
from cpu.constants import DEBUG_OP_PING

# Send PING
await uart_send_byte(dut.i_Clock, dut.i_Uart_Tx_In, dut.cpu.debug.uart_rx.o_Rx_DV, DEBUG_OP_PING)

# Wait for response
response = await uart_wait_for_byte(dut.i_Clock, dut.o_Uart_Rx_Out, dut.cpu.debug.uart_tx.o_Tx_Done)

assert response == 0xAA  # PING_RESPONSE_BYTE
```

## Pin Assignments

**UART**: See [arty-s7-50.xdc](config/arty-s7-50.xdc)
- TX (FPGA → host): Pin D10, Bank 14, LVCMOS33
- RX (host → FPGA): Pin A9, Bank 14, LVCMOS33

**Bank 14**: 3.3V I/O (separate from Bank 34's 1.35V DDR3)

## Future Extensions

**Register access**: WRITE_PC, READ_REGISTER, WRITE_REGISTER need:
- Ports to CPU register file (`o_Reg_Write_Enable`, `o_Reg_Write_Addr`, `o_Reg_Write_Data`)
- Multi-byte command support (opcode + address + data)
- Currently commented out in [debug_peripheral.v](hdl/debug_peripheral/debug_peripheral.v)

**Memory access**: Read/write arbitrary addresses
**Breakpoints**: Trigger halt on PC match
**Single-step**: Execute one instruction then halt

See commented-out ports in [debug_peripheral.v](hdl/debug_peripheral/debug_peripheral.v) lines 144-176 for register access stubs.
