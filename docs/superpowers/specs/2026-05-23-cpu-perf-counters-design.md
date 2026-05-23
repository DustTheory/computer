# CPU Performance Counters Design

**Date:** 2026-05-23

## Goal

Add lightweight hardware performance counters to the RV32I CPU. The counters are returned as part of the existing `DUMP_STATE` command response — no new opcode. Enables measuring CPI, stall breakdown, and memory error rates.

## Counter Set

7 counters, 32 bytes. All gated on `i_Init_Calib_Complete` — nothing counts before DDR3 calibration. All reset to zero on CPU reset.

| Byte offset (within perf section) | Name | Width | Increment condition |
|-----------------------------------|------|-------|---------------------|
| 0–7  | `cycles` | 64-bit | Every clock tick |
| 8–11 | `instructions_retired` | 32-bit | `w_Retire` pulse |
| 12–15 | `stall_cycles_load` | 32-bit | `w_Stall_S1 && w_S2_Is_Load` |
| 16–19 | `stall_cycles_store` | 32-bit | `w_Stall_S1 && w_S2_Is_Store` |
| 20–23 | `stall_cycles_fetch` | 32-bit | `!w_Instruction_Valid && !r_Flushing_Pipeline && !w_Debug_Stall` |
| 24–27 | `flush_cycles` | 32-bit | `r_Flushing_Pipeline` |
| 28–31 | `mem_errors` | 32-bit | `s_data_memory_axil_bvalid && s_data_memory_axil_bresp != 2'b00` |

All values little-endian.

**Known limitation:** Only write errors (`bresp`) counted. Read errors (`rresp`) not in AXI port list.

**Derived metrics** (computed in debugger tool):
- CPI = `cycles / instructions_retired`
- Stall % = `(stall_cycles_load + stall_cycles_store + stall_cycles_fetch + flush_cycles) / cycles * 100`

## DUMP_STATE Response Extension

`DUMP_STATE` currently returns 2 bytes. It will now return **34 bytes**: the existing 2 pipeline/AXI state bytes followed by the 32 perf counter bytes.

```
Byte 0:   [mem_axi_state(3) | pipeline_flushed(1) | stall_s1(1) | enable_fetch(1) | s2_valid(1) | s3_valid(1)]
Byte 1:   [instr_mem_axi_state(2) | init_calib_complete(1) | 5'b0]
Bytes 2–9:  cycles (64-bit LE)
Bytes 10–13: instructions_retired (32-bit LE)
Bytes 14–17: stall_cycles_load (32-bit LE)
Bytes 18–21: stall_cycles_store (32-bit LE)
Bytes 22–25: stall_cycles_fetch (32-bit LE)
Bytes 26–29: flush_cycles (32-bit LE)
Bytes 30–33: mem_errors (32-bit LE)
```

## Architecture

### Approach

Counters live in `cpu.v` (where all needed signals already exist). They are packed into a 256-bit bus wired to `debug_peripheral` as a new `i_Perf_Counters` input. The `op_DUMP_STATE` handler is extended to stream the 32 extra bytes after the existing 2 state bytes.

### Changes

**`hdl/cpu/cpu.v`**
- Declare 7 counter registers; increment in a new `always @(posedge i_Clock)` block gated on `i_Init_Calib_Complete && !w_Reset`
- Pack into `wire [255:0] w_Perf_Counters`
- Pass to `debug_peripheral` as new port `.i_Perf_Counters(w_Perf_Counters)`

**`hdl/debug_peripheral/debug_peripheral.v`**
- Add `input [255:0] i_Perf_Counters` port
- Extend `op_DUMP_STATE` handler: after existing bytes 0–1 (r_Exec_Counter 0–1), stream bytes 2–33 as `i_Perf_Counters[(r_Exec_Counter-2)*8 +: 8]`, transition to `s_IDLE` at counter 34

**`tools/debugger/ui.go`**
- Update `CmdDumpState` handler: expect 34 bytes, parse existing 2-byte fields from `data[0:2]`, parse perf counters from `data[2:34]`, display combined output

**`tools/debugger/serial.go`**
- Update mock: `op_DUMP_STATE` mock response becomes 34 bytes (2 state + 32 perf)

## Wire Packing

```verilog
wire [255:0] w_Perf_Counters;
assign w_Perf_Counters[63:0]    = r_Perf_Cycles;
assign w_Perf_Counters[95:64]   = r_Perf_Instructions_Retired;
assign w_Perf_Counters[127:96]  = r_Perf_Stall_Load;
assign w_Perf_Counters[159:128] = r_Perf_Stall_Store;
assign w_Perf_Counters[191:160] = r_Perf_Stall_Fetch;
assign w_Perf_Counters[223:192] = r_Perf_Flush_Cycles;
assign w_Perf_Counters[255:224] = r_Perf_Mem_Errors;
```

## Testing

- Extend existing `test_debug_dump_state.py` to assert response is 34 bytes and perf fields are present
- Verify `instructions_retired` counts correctly after running known instructions
- Verify `cycles` advances between two calls
- Existing tests must continue to pass
