# CPU Performance Counters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 7 × 64-bit hardware performance counters to the CPU, appended to the existing `DUMP_STATE` response (58 bytes total: 2 state + 56 perf). All counter values are snapshotted atomically at command receipt to prevent drift during UART transmission.

**Architecture:** Counters live in `cpu.v` as 64-bit registers, gated on `i_Init_Calib_Complete`. They are packed into a 448-bit wire `w_Perf_Counters` and passed to `debug_peripheral` as a new input. The `op_DUMP_STATE` handler latches all counters into a 448-bit snapshot register at r_Exec_Counter==0, then streams 56 bytes from the snapshot after the existing 2 state bytes. The Go debugger's `CmdDumpState` handler is updated to parse 58 bytes.

**Tech Stack:** Verilog, Python/cocotb, Go/bubbletea

---

## File Map

| File | Change |
|------|--------|
| `hdl/cpu/cpu.v` | Add 7 × 64-bit counter registers, `wire [447:0] w_Perf_Counters`, pass to `debug_peripheral` |
| `hdl/debug_peripheral/debug_peripheral.v` | Add `input [447:0] i_Perf_Counters`; add `reg [447:0] r_Perf_Snapshot`; extend `op_DUMP_STATE` to 58 bytes with snapshot |
| `tests/cpu/integration_tests/test_debug_dump_state.py` | Extend: assert 58-byte response, verify perf fields |
| `tools/debugger/ui.go` | Update `CmdDumpState` handler: parse 58 bytes, display perf section |
| `tools/debugger/serial.go` | Update mock: `op_DUMP_STATE` returns 58-byte response |

---

## Task 1: Add performance counters to `cpu.v`

**Files:**
- Modify: `hdl/cpu/cpu.v`

All needed signals are already in scope: `w_Stall_S1`, `w_S2_Is_Load`, `w_S2_Is_Store`, `w_Retire`, `r_Flushing_Pipeline`, `w_Instruction_Valid`, `w_Debug_Stall`, `i_Init_Calib_Complete`, `w_Reset`, `s_data_memory_axil_bvalid`, `s_data_memory_axil_bresp`.

- [ ] **Step 1: Declare counter registers**

Add after the `wire w_Retire = w_Retire_Reg || w_Store_Commit;` line:

```verilog
  // Performance counters
  reg [63:0] r_Perf_Cycles;
  reg [63:0] r_Perf_Instructions_Retired;
  reg [63:0] r_Perf_Stall_Load;
  reg [63:0] r_Perf_Stall_Store;
  reg [63:0] r_Perf_Stall_Fetch;
  reg [63:0] r_Perf_Flush_Cycles;
  reg [63:0] r_Perf_Mem_Errors;
```

- [ ] **Step 2: Add counter always block**

Add immediately after the register declarations:

```verilog
  always @(posedge i_Clock) begin
    if (w_Reset) begin
      r_Perf_Cycles               <= 64'd0;
      r_Perf_Instructions_Retired <= 64'd0;
      r_Perf_Stall_Load           <= 64'd0;
      r_Perf_Stall_Store          <= 64'd0;
      r_Perf_Stall_Fetch          <= 64'd0;
      r_Perf_Flush_Cycles         <= 64'd0;
      r_Perf_Mem_Errors           <= 64'd0;
    end else if (i_Init_Calib_Complete) begin
      r_Perf_Cycles <= r_Perf_Cycles + 1;
      if (w_Retire)
        r_Perf_Instructions_Retired <= r_Perf_Instructions_Retired + 1;
      if (w_Stall_S1 && w_S2_Is_Load)
        r_Perf_Stall_Load <= r_Perf_Stall_Load + 1;
      if (w_Stall_S1 && w_S2_Is_Store)
        r_Perf_Stall_Store <= r_Perf_Stall_Store + 1;
      if (!w_Instruction_Valid && !r_Flushing_Pipeline && !w_Debug_Stall)
        r_Perf_Stall_Fetch <= r_Perf_Stall_Fetch + 1;
      if (r_Flushing_Pipeline)
        r_Perf_Flush_Cycles <= r_Perf_Flush_Cycles + 1;
      if (s_data_memory_axil_bvalid && s_data_memory_axil_bresp != 2'b00)
        r_Perf_Mem_Errors <= r_Perf_Mem_Errors + 1;
    end
  end
```

- [ ] **Step 3: Declare and assign packed wire**

Add after the always block:

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

- [ ] **Step 4: Pass bus to `debug_peripheral` instantiation**

In the `debug_peripheral debug_peripheral (...)` instantiation, add after `.i_Init_Calib_Complete(i_Init_Calib_Complete),`:

```verilog
      .i_Perf_Counters(w_Perf_Counters),
```

- [ ] **Step 5: Verify existing tests pass**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=integration
```

Expected: all pass (counters tick silently, nothing reads them yet).

- [ ] **Step 6: Commit**

```bash
git add hdl/cpu/cpu.v
git commit -m "feat: add 64-bit performance counter registers to cpu.v"
```

---

## Task 2: Extend `op_DUMP_STATE` handler in `debug_peripheral`

**Files:**
- Modify: `hdl/debug_peripheral/debug_peripheral.v`

Currently `op_DUMP_STATE` streams 2 bytes (r_Exec_Counter 0–1) then goes idle. We extend it to:
- At r_Exec_Counter == 0: latch `i_Perf_Counters` into `r_Perf_Snapshot`, queue state byte 0
- At r_Exec_Counter == 1: queue state byte 1
- At r_Exec_Counter 2–57: queue `r_Perf_Snapshot[(r_Exec_Counter-2)*8 +: 8]`
- At r_Exec_Counter >= 58: go to `s_IDLE`

- [ ] **Step 1: Add `i_Perf_Counters` input port and `r_Perf_Snapshot` register**

In the module port list, add after `o_Write_PC_Data`:

```verilog
    input [447:0] i_Perf_Counters
```

In the `/* ----------------DEBUG PERIPHERAL LOGIC---------------- */` section, add after `reg [31:0] r_Exec_Counter = 0;`:

```verilog
  reg [447:0] r_Perf_Snapshot;
```

- [ ] **Step 2: Replace `op_DUMP_STATE` case**

Replace the entire existing `op_DUMP_STATE` case with:

```verilog
            op_DUMP_STATE: begin
              case (r_Exec_Counter)
                0: begin
                  r_Perf_Snapshot <= i_Perf_Counters;
                  output_buffer[output_buffer_head] <= {
                    i_Mem_AXI_State,
                    i_Pipeline_Flushed,
                    i_Stall_S1,
                    i_Enable_Instruction_Fetch,
                    i_S2_Valid,
                    i_S3_Valid
                  };
                  output_buffer_head <= output_buffer_head + 1;
                end
                1: begin
                  output_buffer[output_buffer_head] <= {
                    i_Instr_Mem_AXI_State,
                    i_Init_Calib_Complete,
                    5'b0
                  };
                  output_buffer_head <= output_buffer_head + 1;
                end
                default: begin
                  if (r_Exec_Counter < 58) begin
                    output_buffer[output_buffer_head] <= r_Perf_Snapshot[(r_Exec_Counter - 2) * 8 +: 8];
                    output_buffer_head <= output_buffer_head + 1;
                  end else begin
                    r_State <= s_IDLE;
                  end
                end
              endcase
            end
```

- [ ] **Step 3: Verify existing tests pass**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=integration
```

Expected: all pass (existing `test_debug_dump_state.py` reads only 2 bytes — it will still pass since the extra bytes are just queued in the output buffer and not yet consumed by the test).

- [ ] **Step 4: Commit**

```bash
git add hdl/debug_peripheral/debug_peripheral.v
git commit -m "feat: extend DUMP_STATE to snapshot and stream 56 perf counter bytes"
```

---

## Task 3: Extend `test_debug_dump_state.py`

**Files:**
- Modify: `tests/cpu/integration_tests/test_debug_dump_state.py`

The existing test reads 2 bytes via `uart_wait_for_byte`. Extend it to read 58 bytes total and verify the perf section.

- [ ] **Step 1: Read the current test**

```bash
cat /home/emma/gpu/tests/cpu/integration_tests/test_debug_dump_state.py
```

- [ ] **Step 2: Add `import struct` if not already present**

At the top of the test file, add:

```python
import struct
```

- [ ] **Step 3: Read 56 more bytes after the existing 2, and assert sanity**

After the existing `byte0`/`byte1` assertions, append:

```python
    # Read 56 perf counter bytes (7 x 64-bit little-endian)
    perf_bytes = []
    for _ in range(56):
        b = await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )
        perf_bytes.append(b)

    cycles               = struct.unpack_from('<Q', bytes(perf_bytes[0:8]))[0]
    instructions_retired = struct.unpack_from('<Q', bytes(perf_bytes[8:16]))[0]
    stall_cycles_load    = struct.unpack_from('<Q', bytes(perf_bytes[16:24]))[0]
    stall_cycles_store   = struct.unpack_from('<Q', bytes(perf_bytes[24:32]))[0]
    stall_cycles_fetch   = struct.unpack_from('<Q', bytes(perf_bytes[32:40]))[0]
    flush_cycles         = struct.unpack_from('<Q', bytes(perf_bytes[40:48]))[0]
    mem_errors           = struct.unpack_from('<Q', bytes(perf_bytes[48:56]))[0]

    # i_Init_Calib_Complete = 1 in harness so cycles must be > 0
    assert cycles > 0, f"cycles should be > 0, got {cycles}"
    # No bad AXI responses in test harness
    assert mem_errors == 0, f"mem_errors should be 0, got {mem_errors}"
    # Stall counters must not exceed total cycles
    assert stall_cycles_load  <= cycles, f"stall_cycles_load {stall_cycles_load} > cycles {cycles}"
    assert stall_cycles_store <= cycles, f"stall_cycles_store {stall_cycles_store} > cycles {cycles}"
    assert stall_cycles_fetch <= cycles, f"stall_cycles_fetch {stall_cycles_fetch} > cycles {cycles}"
    assert flush_cycles       <= cycles, f"flush_cycles {flush_cycles} > cycles {cycles}"
```

- [ ] **Step 4: Run the extended test**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=integration TEST_FILE=test_debug_dump_state
```

Expected: PASS.

- [ ] **Step 5: Run full test suite**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=all
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add tests/cpu/integration_tests/test_debug_dump_state.py
git commit -m "test: extend test_debug_dump_state to verify 56-byte perf counter section"
```

---

## Task 4: Update Go debugger

**Files:**
- Modify: `tools/debugger/ui.go`
- Modify: `tools/debugger/serial.go`

The `CmdDumpState` handler in `ui.go` currently reads 2 bytes. It must now accept 58 bytes. The mock in `serial.go` must return 58 bytes.

- [ ] **Step 1: Update mock in `serial.go`**

In `SendCommand`, find the `time.AfterFunc` mock block and replace it:

```go
time.AfterFunc(50*time.Millisecond, func() {
    var mockData []byte
    if opcode == op_DUMP_STATE {
        mockData = make([]byte, 58)
        // byte0: data mem IDLE, all pipeline flags clear
        mockData[0] = 0x00
        // byte1: instr mem IDLE, init_calib_complete=1 (bit 5)
        mockData[1] = 0x20
        // perf counters: cycles=1000000, instructions=500000, rest 0
        // cycles at bytes 2-9 (little-endian uint64)
        cycles := uint64(1000000)
        for i := 0; i < 8; i++ {
            mockData[2+i] = byte(cycles >> (i * 8))
        }
        // instructions_retired at bytes 10-17
        retired := uint64(500000)
        for i := 0; i < 8; i++ {
            mockData[10+i] = byte(retired >> (i * 8))
        }
        // remaining counters stay 0
    } else {
        mockData = []byte{byte(opcode), 0xAA, 0x55}
    }
    sm.handleResponse(mockData)
})
```

- [ ] **Step 2: Update `CmdDumpState` handler in `ui.go`**

Find the `if cmd == CmdDumpState {` block and replace it entirely:

```go
		// For DUMP_STATE, wait for 58-byte response (2 state bytes + 56 perf counter bytes)
		if cmd == CmdDumpState {
			time.Sleep(600 * time.Millisecond)

			responses := m.serialMgr.GetResponses()
			if len(responses) > 0 {
				lastResp := responses[len(responses)-1]
				if len(lastResp.Data) >= 58 {
					b0 := lastResp.Data[0]
					b1 := lastResp.Data[1]
					p := lastResp.Data[2:58]

					dataMemStateNames := []string{
						"IDLE", "READ_SUBMITTING", "READ_AWAITING", "READ_SUCCESS",
						"WRITE_SUBMITTING", "WRITE_AWAITING", "WRITE_SUCCESS", "MEMORY_ERROR",
					}
					instrMemStateNames := []string{
						"IDLE", "READ_SUBMITTING", "READ_AWAITING", "READ_SUCCESS",
					}
					dataMemState      := (b0 >> 5) & 0x7
					pipelineFlushed   := (b0 >> 4) & 0x1
					stallS1           := (b0 >> 3) & 0x1
					enableFetch       := (b0 >> 2) & 0x1
					s2Valid           := (b0 >> 1) & 0x1
					s3Valid           := b0 & 0x1
					instrMemState     := (b1 >> 6) & 0x3
					initCalibComplete := (b1 >> 5) & 0x1

					u64 := func(b []byte, off int) uint64 {
						var v uint64
						for i := 0; i < 8; i++ {
							v |= uint64(b[off+i]) << (i * 8)
						}
						return v
					}
					cycles      := u64(p, 0)
					retired     := u64(p, 8)
					stallLoad   := u64(p, 16)
					stallStore  := u64(p, 24)
					stallFetch  := u64(p, 32)
					flushCycles := u64(p, 40)
					memErrors   := u64(p, 48)

					var cpi float64
					if retired > 0 {
						cpi = float64(cycles) / float64(retired)
					}
					totalStall := stallLoad + stallStore + stallFetch + flushCycles
					var stallPct float64
					if cycles > 0 {
						stallPct = float64(totalStall) / float64(cycles) * 100
					}
					pct := func(v uint64) float64 {
						if cycles == 0 { return 0 }
						return float64(v) / float64(cycles) * 100
					}

					msg := fmt.Sprintf(
						"✓ State dump:\n"+
							"  data_mem_axi:      %s\n"+
							"  instr_mem_axi:     %s\n"+
							"  init_calib:        %d\n"+
							"  pipeline_flushed:  %d\n"+
							"  stall_s1:          %d\n"+
							"  enable_fetch:      %d\n"+
							"  s2_valid:          %d\n"+
							"  s3_valid:          %d\n"+
							"─────────────────────────────────\n"+
							"  cycles:            %d\n"+
							"  instructions:      %d\n"+
							"  CPI:               %.2f\n"+
							"  stall%% (load):     %.1f%%\n"+
							"  stall%% (store):    %.1f%%\n"+
							"  stall%% (fetch):    %.1f%%\n"+
							"  flush%%:            %.1f%%\n"+
							"  total stall%%:      %.1f%%\n"+
							"  mem_errors:        %d",
						dataMemStateNames[dataMemState], instrMemStateNames[instrMemState],
						initCalibComplete, pipelineFlushed, stallS1, enableFetch, s2Valid, s3Valid,
						cycles, retired, cpi,
						pct(stallLoad), pct(stallStore), pct(stallFetch), pct(flushCycles),
						stallPct, memErrors,
					)
					return commandCompleteMsg{success: true, message: msg, cmd: cmd}
				}
			}

			return commandCompleteMsg{
				success: false,
				message: "Failed to read state dump (expected 58 bytes)",
				cmd:     cmd,
			}
		}
```

- [ ] **Step 3: Build and verify it compiles**

```bash
cd /home/emma/gpu/tools && go build ./debugger
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add tools/debugger/ui.go tools/debugger/serial.go
git commit -m "feat: update DUMP_STATE Go handler to parse 58-byte response with perf counters"
```

---

## Task 5: Final verification

- [ ] **Step 1: Run full test suite**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=all
```

Expected: all pass.

- [ ] **Step 2: Build debugger**

```bash
cd /home/emma/gpu/tools && go build ./debugger
```

Expected: clean build.

- [ ] **Step 3: Smoke test with mock port**

```bash
cd /home/emma/gpu/tools && go run ./debugger
```

Select `[Mock Port - Testing Only]`, connect, navigate to `Dump State`, press Enter. Expected: 58-byte response parsed, CPI ~2.00 displayed (1,000,000 cycles / 500,000 instructions).
