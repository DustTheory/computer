# Debug Protocol

**Last updated**: 2026-01-02  
**Source files**: `hdl/debug_peripheral/debug_peripheral.v`, `hdl/debug_peripheral/debug_peripheral.vh`, `tools/debugger/`  
**Related docs**: [cpu-architecture.md](cpu-architecture.md)

---

Complete specification of the UART debug peripheral for CPU control.

## Overview

The debug peripheral allows external control of the CPU via UART commands (115200 baud, 8N1). It can halt/unhalt CPU execution, reset the CPU, and respond to ping requests.

**Module**: `hdl/debug_peripheral/debug_peripheral.v`

**Ports**:
- `i_Uart_Tx_In` - UART RX from host (host transmits to FPGA)
- `o_Uart_Rx_Out` - UART TX to host (FPGA transmits to host)
- `o_Halt_Cpu` - Stops CPU clock when high
- `o_Reset_Cpu` - Holds CPU in reset when high

## Protocol

### Command Format

**Single-byte commands**: Send 1 byte opcode, debug peripheral executes immediately.

| Opcode | Command | Description | Response |
|--------|---------|-------------|----------|
| `0x00` | NOP | No operation | None |
| `0x01` | RESET | Assert CPU reset (`o_Reset_Cpu = 1`) | None |
| `0x02` | UNRESET | Deassert CPU reset (`o_Reset_Cpu = 0`) | None |
| `0x03` | HALT | Halt CPU (`o_Halt_Cpu = 1`) | None |
| `0x04` | UNHALT | Resume CPU (`o_Halt_Cpu = 0`) | None |
| `0x05` | PING | Test connectivity | `0xAA` |

### State Machine

**States** (from `debug_peripheral.vh`):
- `s_IDLE (0)` - Waiting for command byte
- `s_DECODE_AND_EXECUTE (1)` - Executing received opcode

**Flow**:
1. Start in `s_IDLE`
2. On `w_Rx_DV` (UART byte received), latch `w_Rx_Byte` into `r_Op_Code`, transition to `s_DECODE_AND_EXECUTE`
3. In `s_DECODE_AND_EXECUTE`, execute command based on `r_Op_Code`:
   - **NOP**: Do nothing, return to `s_IDLE`
   - **RESET**: Set `o_Reset_Cpu = 1`, return to `s_IDLE`
   - **UNRESET**: Set `o_Reset_Cpu = 0`, return to `s_IDLE`
   - **HALT**: Set `o_Halt_Cpu = 1`, return to `s_IDLE`
   - **UNHALT**: Set `o_Halt_Cpu = 0`, return to `s_IDLE`
   - **PING**: Set `r_Tx_Byte = 0xAA`, pulse `r_Tx_DV`, wait for `w_Tx_Done`, return to `s_IDLE`
4. Return to `s_IDLE` when command complete

### PING Response

**Purpose**: Verify FPGA is responsive and UART link is working.

**Process**:
1. Host sends `0x05` byte
2. Debug peripheral receives opcode, enters `s_DECODE_AND_EXECUTE`
3. On first cycle (`r_Exec_Counter == 0`): Set `r_Tx_Byte = 0xAA`, `r_Tx_DV = 1`
4. On subsequent cycles: Clear `r_Tx_DV`, wait for UART transmitter to assert `w_Tx_Done`
5. When `w_Tx_Done` high, return to `s_IDLE`
6. Host receives `0xAA` byte

**Response byte**: `0xAA` (defined as `PING_RESPONSE_BYTE` in `debug_peripheral.vh`)

## UART Timing

**Baud rate**: 115200 bps

**Clocks per bit**: For 100 MHz clock = 100,000,000 / 115,200 ≈ 868 clocks

**Modules**: `uart_receiver.v` (RX), `uart_transmitter.v` (TX)

**Interface**:
- **RX**: Asserts `o_Rx_DV` for 1 cycle when byte received, `o_Rx_Byte` contains data
- **TX**: Assert `i_Tx_DV` for 1 cycle with `i_Tx_Byte` data, wait for `o_Tx_Done` to pulse

## Go Debugger Tool

**Location**: `tools/debugger/`

**Run**: `go run tools/debugger/main.go`

**Implemented commands**:
- ✓ Halt CPU
- ✓ Unhalt CPU
- ✓ Reset CPU
- ✓ Unreset CPU
- ✓ Ping CPU

**Unimplemented**:
- ✗ Read Register
- ✗ Full Dump
- ✗ Set Register
- ✗ Jump to Address
- ✗ Load Program

**Opcode constants** (from `opcodes.go`):
```go
op_NOP     = 0x0
op_RESET   = 0x1
op_UNRESET = 0x2
op_HALT    = 0x3
op_UNHALT  = 0x4
op_PING    = 0x5
```

## Commented-Out Features

**Register read/write ports** (in `debug_peripheral.v`):
```verilog
// output o_Reg_Write_Enable,
// output [4:0] o_Reg_Write_Addr,
// output [31:0] o_Reg_Write_Data,

// output o_Reg_Read_Enable,
// output [4:0] o_Reg_Read_Addr,
// input [31:0] i_Reg_Read_Data
```

**Status**: Commented out, not connected to CPU register file.

## Testing

**File**: `tests/cpu/integration_tests/test_debug_peripheral.py`

**Tests**:
- ✓ CPU halts when HALT command sent
- ✓ CPU resumes when UNHALT command sent
- ✓ CPU resets when RESET command sent
- ✓ PING returns `0xAA` response

## Known Issues

**⚠ spec.txt is outdated**: The file `hdl/debug_peripheral/spec.txt` does not match current implementation. Use this document and the Verilog source as ground truth.

**No error handling**: Invalid opcodes transition back to `s_IDLE` without response.

**No multi-byte commands**: Future register read/write needs framing protocol.

## Usage Examples

### Python (cocotb)
```python
def uart_encode_byte(byte_val):
    bits = [0]  # Start bit
    for i in range(8):
        bits.append((byte_val >> i) & 1)
    bits.append(1)  # Stop bit
    return bits

# Send HALT
for bit in uart_encode_byte(0x03):
    dut.i_Uart_Tx_In.value = bit
    await ClockCycles(dut.i_Clock, UART_CLOCKS_PER_BIT)
```

### Bash
```bash
stty -F /dev/ttyUSB1 115200 cs8 -cstopb -parenb raw
echo -ne '\x05' > /dev/ttyUSB1  # Send PING
dd if=/dev/ttyUSB1 bs=1 count=1 2>/dev/null | xxd -p  # Read 0xAA
```
