# CPU Performance Counters Design

**Date:** 2026-05-23

## Goal

Add lightweight hardware performance counters to the RV32I CPU, readable via a new `STATS_DUMP` debug command. Enables measuring CPI, stall breakdown, and memory error rates without a logic analyser.

## Counter Set

8 counters, 32 bytes total over UART. All gated on `i_Init_Calib_Complete` — nothing counts before DDR3 calibration completes. All reset to zero on CPU reset.

| Byte offset | Name | Width | Increment condition |
|-------------|------|-------|---------------------|
| 0–7 | `cycles` | 64-bit | Every clock tick |
| 8–11 | `instructions_retired` | 32-bit | `w_Retire` pulse |
| 12–15 | `stall_cycles_load` | 32-bit | `w_Stall_S1 && w_S2_Is_Load` |
| 16–19 | `stall_cycles_store` | 32-bit | `w_Stall_S1 && w_S2_Is_Store` |
| 20–23 | `stall_cycles_fetch` | 32-bit | `!w_Instruction_Valid && !r_Flushing_Pipeline && !w_Debug_Stall` |
| 24–27 | `flush_cycles` | 32-bit | `r_Flushing_Pipeline` |
| 28–31 | `mem_errors` | 32-bit | `s_data_memory_axil_bvalid && s_data_memory_axil_bresp != 2'b00` |

All values are little-endian in the UART response.

**Known limitation:** Only write errors (`bresp`) are counted. Read errors (`rresp`) are not currently in the AXI port list and would require adding `rresp` through `cpu.v`, `memory_axi.v`, and the top-level interconnect. Left for a future change.

**Derived metrics** (computed in the debugger tool):
- CPI = `cycles / instructions_retired`
- Stall % = `(stall_cycles_load + stall_cycles_store + stall_cycles_fetch + flush_cycles) / cycles * 100`

## Architecture

### Approach

Counters live in `cpu.v` (Option A). All signals needed are already available there. The packed counter bus is passed to `debug_peripheral` as a new input. No new modules.

### Changes

**`hdl/cpu/cpu.v`**
- Add 8 counter registers
- Increment each on the appropriate condition inside an `always @(posedge i_Clock)` block gated on `i_Init_Calib_Complete && !w_Reset`
- Expose as `w_Perf_Counters [255:0]` (packed, byte 0 = cycles[7:0])
- Wire to `debug_peripheral` as new input `i_Perf_Counters`

**`hdl/debug_peripheral/debug_peripheral.vh`**
- Add `op_STATS_DUMP = 8'h0A`

**`hdl/debug_peripheral/debug_peripheral.v`**
- Add `input [255:0] i_Perf_Counters` port
- Add `op_STATS_DUMP` handler: loop `r_Exec_Counter` 0–31, write `i_Perf_Counters[r_Exec_Counter*8 +: 8]` each tick, return to `s_IDLE` at 32. Same pattern as `op_READ_PC`.

**`tools/debugger/commands.go`**
- Add `op_STATS_DUMP = 0x0A` to opcodes
- Add `GetOpCode()` case for `CmdStatsDump`
- Mark `CmdStatsDump` as `implemented: true`

**`tools/debugger/ui.go`** (or new `tools/debugger/stats.go`)
- Add `CmdStatsDump` handler: read 32 bytes, parse fields, display table with raw counts and derived CPI / stall % metrics

## Wire Packing

```verilog
wire [255:0] w_Perf_Counters;
assign w_Perf_Counters[63:0]   = r_Cycles;
assign w_Perf_Counters[95:64]  = r_Instructions_Retired;
assign w_Perf_Counters[127:96] = r_Stall_Cycles_Load;
assign w_Perf_Counters[159:128] = r_Stall_Cycles_Store;
assign w_Perf_Counters[191:160] = r_Stall_Cycles_Fetch;
assign w_Perf_Counters[223:192] = r_Flush_Cycles;
assign w_Perf_Counters[255:224] = r_Mem_Errors;
```

## Testing

- Existing unit/integration tests must continue to pass (no behavioral change to CPU)
- Manual test: load a simple program, run `STATS_DUMP`, verify `instructions_retired` matches expected retire count, `cycles >= instructions_retired`
- Verify counters stay zero before DDR3 calib (hard to test in sim, note as manual FPGA check)
