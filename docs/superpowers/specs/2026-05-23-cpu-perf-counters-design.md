# CPU Performance Counters Design

**Date:** 2026-05-23

## Goal

Add lightweight hardware performance counters to the RV32I CPU. The counters are returned as part of the existing `DUMP_STATE` command response — no new opcode. Enables measuring CPI, stall breakdown, and memory error rates.

## Counter Set

7 counters, all 64-bit. All gated on `i_Init_Calib_Complete` — nothing counts before DDR3 calibration. All reset to zero on CPU reset.

| Byte offset (within perf section) | Name | Increment condition |
|-----------------------------------|------|---------------------|
| 0–7   | `cycles`               | Every clock tick |
| 8–15  | `instructions_retired` | `w_Retire` pulse |
| 16–23 | `stall_cycles_load`    | `w_Stall_S1 && w_S2_Is_Load` |
| 24–31 | `stall_cycles_store`   | `w_Stall_S1 && w_S2_Is_Store` |
| 32–39 | `stall_cycles_fetch`   | `!w_Instruction_Valid && !r_Flushing_Pipeline && !w_Debug_Stall` |
| 40–47 | `flush_cycles`         | `r_Flushing_Pipeline` |
| 48–55 | `mem_errors`           | `s_data_memory_axil_bvalid && s_data_memory_axil_bresp != 2'b00` |

All values little-endian.

**Known limitation:** Only write errors (`bresp`) counted. Read errors (`rresp`) not in AXI port list.

**Derived metrics** (computed in debugger tool):
- CPI = `cycles / instructions_retired`
- Stall % = `(stall_cycles_load + stall_cycles_store + stall_cycles_fetch + flush_cycles) / cycles * 100`

## DUMP_STATE Response Extension

`DUMP_STATE` currently returns 2 bytes. It will now return **58 bytes**: the existing 2 pipeline/AXI state bytes followed by 56 perf counter bytes.

```
Byte 0:    [mem_axi_state(3) | pipeline_flushed(1) | stall_s1(1) | enable_fetch(1) | s2_valid(1) | s3_valid(1)]
Byte 1:    [instr_mem_axi_state(2) | init_calib_complete(1) | 5'b0]
Bytes 2–57: perf counters (56 bytes, snapshotted atomically — see below)
```

## Snapshot Requirement

UART transmission of 56 bytes takes ~395,000 clocks at 81.25 MHz (706 clocks/bit × 10 bits/byte × 56 bytes). Streaming live registers would mean the first and last bytes differ by ~40k cycles. To prevent this, all counter values are latched into a **snapshot register** in `debug_peripheral` at the moment `op_DUMP_STATE` is received (r_Exec_Counter == 0), before any bytes are queued. The stream is then read entirely from the snapshot.

## Architecture

### Approach

Counters live in `cpu.v` (all needed signals already exist there). They are packed into a 448-bit wire (`w_Perf_Counters [447:0]`) and passed to `debug_peripheral` as a new input. The `op_DUMP_STATE` handler latches the wire into a 448-bit snapshot register on the first execution cycle, then streams bytes from the snapshot.

### Changes

**`hdl/cpu/cpu.v`**
- Declare 7 × 64-bit counter registers
- Increment in a new `always @(posedge i_Clock)` block gated on `i_Init_Calib_Complete && !w_Reset`
- Pack into `wire [447:0] w_Perf_Counters`
- Pass to `debug_peripheral` as new port `.i_Perf_Counters(w_Perf_Counters)`

**`hdl/debug_peripheral/debug_peripheral.v`**
- Add `input [447:0] i_Perf_Counters` port
- Add `reg [447:0] r_Perf_Snapshot` register
- In `op_DUMP_STATE` at r_Exec_Counter == 0: latch `r_Perf_Snapshot <= i_Perf_Counters` and queue state byte 0
- At r_Exec_Counter == 1: queue state byte 1
- At r_Exec_Counter 2–57: queue `r_Perf_Snapshot[(r_Exec_Counter-2)*8 +: 8]`
- At r_Exec_Counter >= 58: transition to `s_IDLE`

**`tools/debugger/ui.go`**
- Update `CmdDumpState` handler: expect 58 bytes, parse 2-byte state fields from `data[0:2]`, parse 7 × 64-bit counters from `data[2:58]`, display combined output

**`tools/debugger/serial.go`**
- Update mock: `op_DUMP_STATE` mock response becomes 58 bytes

## Wire Packing

```verilog
wire [447:0] w_Perf_Counters;
assign w_Perf_Counters[63:0]    = r_Perf_Cycles;
assign w_Perf_Counters[127:64]  = r_Perf_Instructions_Retired;
assign w_Perf_Counters[191:128] = r_Perf_Stall_Load;
assign w_Perf_Counters[255:192] = r_Perf_Stall_Store;
assign w_Perf_Counters[319:256] = r_Perf_Stall_Fetch;
assign w_Perf_Counters[383:320] = r_Perf_Flush_Cycles;
assign w_Perf_Counters[447:384] = r_Perf_Mem_Errors;
```

## Testing

- Extend existing `test_debug_dump_state.py` to assert response is 58 bytes and perf fields are sane
- Verify `cycles` > 0 after reset (i_Init_Calib_Complete = 1 in harness)
- Verify `mem_errors` = 0 when no bad AXI responses occur
- Existing tests must continue to pass
