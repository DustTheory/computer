# CPU Performance Counters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 7 hardware performance counters to the CPU, appended to the existing `DUMP_STATE` response (34 bytes total instead of 2), with updated display in the Go debugger.

**Architecture:** Counters live in `cpu.v` as plain registers, gated on `i_Init_Calib_Complete`. They are packed into a 256-bit bus passed to `debug_peripheral` as a new `i_Perf_Counters` input. The existing `op_DUMP_STATE` handler is extended to stream the 32 extra counter bytes after the existing 2 state bytes. The Go debugger's `CmdDumpState` handler is updated to expect 34 bytes and display both sections.

**Tech Stack:** Verilog, Python/cocotb, Go/bubbletea

---

## File Map

| File | Change |
|------|--------|
| `hdl/cpu/cpu.v` | Add 7 counter registers, packed bus `w_Perf_Counters[255:0]`, pass to `debug_peripheral` |
| `hdl/debug_peripheral/debug_peripheral.v` | Add `i_Perf_Counters[255:0]` port; extend `op_DUMP_STATE` handler to 34 bytes |
| `tests/cpu/integration_tests/test_debug_dump_state.py` | Extend: assert 34-byte response, verify perf fields |
| `tools/debugger/ui.go` | Update `CmdDumpState` handler: parse 34 bytes, display perf section |
| `tools/debugger/serial.go` | Update mock: `op_DUMP_STATE` returns 34-byte response |

---

## Task 1: Add performance counters to `cpu.v`

**Files:**
- Modify: `hdl/cpu/cpu.v`

All needed signals are already in scope in `cpu.v`: `w_Stall_S1`, `w_S2_Is_Load`, `w_S2_Is_Store`, `w_Retire`, `r_Flushing_Pipeline`, `w_Instruction_Valid`, `w_Debug_Stall`, `i_Init_Calib_Complete`, `w_Reset`, `s_data_memory_axil_bvalid`, `s_data_memory_axil_bresp`.

- [ ] **Step 1: Declare counter registers**

Add after the `wire w_Retire = w_Retire_Reg || w_Store_Commit;` line:

```verilog
  // Performance counters
  reg [63:0] r_Perf_Cycles;
  reg [31:0] r_Perf_Instructions_Retired;
  reg [31:0] r_Perf_Stall_Load;
  reg [31:0] r_Perf_Stall_Store;
  reg [31:0] r_Perf_Stall_Fetch;
  reg [31:0] r_Perf_Flush_Cycles;
  reg [31:0] r_Perf_Mem_Errors;
```

- [ ] **Step 2: Add counter always block**

Add immediately after the register declarations:

```verilog
  always @(posedge i_Clock) begin
    if (w_Reset) begin
      r_Perf_Cycles               <= 64'd0;
      r_Perf_Instructions_Retired <= 32'd0;
      r_Perf_Stall_Load           <= 32'd0;
      r_Perf_Stall_Store          <= 32'd0;
      r_Perf_Stall_Fetch          <= 32'd0;
      r_Perf_Flush_Cycles         <= 32'd0;
      r_Perf_Mem_Errors           <= 32'd0;
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
  wire [255:0] w_Perf_Counters;
  assign w_Perf_Counters[63:0]    = r_Perf_Cycles;
  assign w_Perf_Counters[95:64]   = r_Perf_Instructions_Retired;
  assign w_Perf_Counters[127:96]  = r_Perf_Stall_Load;
  assign w_Perf_Counters[159:128] = r_Perf_Stall_Store;
  assign w_Perf_Counters[191:160] = r_Perf_Stall_Fetch;
  assign w_Perf_Counters[223:192] = r_Perf_Flush_Cycles;
  assign w_Perf_Counters[255:224] = r_Perf_Mem_Errors;
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

Expected: all pass (counters increment silently, nothing reads them yet).

- [ ] **Step 6: Commit**

```bash
git add hdl/cpu/cpu.v
git commit -m "feat: add performance counter registers to cpu.v"
```

---

## Task 2: Extend `op_DUMP_STATE` handler in `debug_peripheral`

**Files:**
- Modify: `hdl/debug_peripheral/debug_peripheral.v`

Currently `op_DUMP_STATE` streams 2 bytes (r_Exec_Counter 0 and 1) then goes to `s_IDLE` at `default`. We extend it to stream 32 more bytes (counter 2–33) before going idle.

The existing handler:
```verilog
op_DUMP_STATE: begin
  case (r_Exec_Counter)
    0: begin
      output_buffer[output_buffer_head] <= { i_Mem_AXI_State, i_Pipeline_Flushed, i_Stall_S1, i_Enable_Instruction_Fetch, i_S2_Valid, i_S3_Valid };
      output_buffer_head <= output_buffer_head + 1;
    end
    1: begin
      output_buffer[output_buffer_head] <= { i_Instr_Mem_AXI_State, i_Init_Calib_Complete, 5'b0 };
      output_buffer_head <= output_buffer_head + 1;
    end
    default: begin
      r_State <= s_IDLE;
    end
  endcase
end
```

- [ ] **Step 1: Add `i_Perf_Counters` input port**

In the module port list, add after `o_Write_PC_Data`:

```verilog
    input [255:0] i_Perf_Counters
```

- [ ] **Step 2: Replace `op_DUMP_STATE` case**

Replace the entire `op_DUMP_STATE` case with:

```verilog
            op_DUMP_STATE: begin
              case (r_Exec_Counter)
                0: begin
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
                  if (r_Exec_Counter < 34) begin
                    output_buffer[output_buffer_head] <= i_Perf_Counters[(r_Exec_Counter - 2) * 8 +: 8];
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

Expected: all pass. Note: `test_debug_dump_state.py` may now fail because it only reads 2 bytes — that will be fixed in Task 3.

- [ ] **Step 4: Commit**

```bash
git add hdl/debug_peripheral/debug_peripheral.v
git commit -m "feat: extend DUMP_STATE to append 32 perf counter bytes"
```

---

## Task 3: Extend `test_debug_dump_state.py`

**Files:**
- Modify: `tests/cpu/integration_tests/test_debug_dump_state.py`

The existing test sends `DUMP_STATE` and reads 2 bytes via `uart_wait_for_byte`. It needs to read 34 bytes and verify the perf section is present and sane.

Read the current test first: `tests/cpu/integration_tests/test_debug_dump_state.py`

- [ ] **Step 1: Read the existing test**

```bash
cat /home/emma/gpu/tests/cpu/integration_tests/test_debug_dump_state.py
```

- [ ] **Step 2: Add perf counter assertions to existing test**

After the existing 2-byte receive and assertions, add reading 32 more bytes and basic sanity checks. Add these imports at the top if not already present:

```python
import struct
```

After the existing `byte0`/`byte1` assertions, append:

```python
    # Read 32 perf counter bytes
    perf_bytes = []
    for _ in range(32):
        b = await uart_wait_for_byte(
            dut.i_Clock,
            dut.cpu.o_Uart_Rx_Out,
            dut.cpu.debug_peripheral.uart_transmitter.o_Tx_Done
        )
        perf_bytes.append(b)

    cycles               = struct.unpack_from('<Q', bytes(perf_bytes[0:8]))[0]
    instructions_retired = struct.unpack_from('<I', bytes(perf_bytes[8:12]))[0]
    stall_cycles_load    = struct.unpack_from('<I', bytes(perf_bytes[12:16]))[0]
    stall_cycles_store   = struct.unpack_from('<I', bytes(perf_bytes[16:20]))[0]
    stall_cycles_fetch   = struct.unpack_from('<I', bytes(perf_bytes[20:24]))[0]
    flush_cycles         = struct.unpack_from('<I', bytes(perf_bytes[24:28]))[0]
    mem_errors           = struct.unpack_from('<I', bytes(perf_bytes[28:32]))[0]

    # i_Init_Calib_Complete = 1 in harness so cycles must be > 0
    assert cycles > 0, f"cycles should be > 0, got {cycles}"
    # No memory ops have run, errors should be 0
    assert mem_errors == 0, f"mem_errors should be 0, got {mem_errors}"
    # Sanity: stall counters don't exceed cycles
    assert stall_cycles_load <= cycles, "stall_cycles_load > cycles"
    assert stall_cycles_store <= cycles, "stall_cycles_store > cycles"
    assert stall_cycles_fetch <= cycles, "stall_cycles_fetch > cycles"
    assert flush_cycles <= cycles, "flush_cycles > cycles"
```

- [ ] **Step 3: Run the updated test**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=integration TEST_FILE=test_debug_dump_state
```

Expected: PASS.

- [ ] **Step 4: Run full test suite**

```bash
cd /home/emma/gpu/tests && source test_env/bin/activate && make TEST_TYPE=all
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tests/cpu/integration_tests/test_debug_dump_state.py
git commit -m "test: extend test_debug_dump_state to verify perf counter bytes"
```

---

## Task 4: Update Go debugger

**Files:**
- Modify: `tools/debugger/ui.go`
- Modify: `tools/debugger/serial.go`

The `CmdDumpState` handler in `ui.go` currently reads 2 bytes. It must now accept 34 bytes and display the perf section. The mock in `serial.go` must return 34 bytes.

- [ ] **Step 1: Update mock in `serial.go`**

In `SendCommand`, find the `time.AfterFunc` mock block:

```go
time.AfterFunc(50*time.Millisecond, func() {
    mockData := []byte{byte(opcode), 0xAA, 0x55}
    sm.handleResponse(mockData)
})
```

Replace with:

```go
time.AfterFunc(50*time.Millisecond, func() {
    var mockData []byte
    if opcode == op_DUMP_STATE {
        mockData = make([]byte, 34)
        // byte0: all flags clear, data mem IDLE (state=0)
        mockData[0] = 0x00
        // byte1: instr mem IDLE, init_calib_complete=1
        mockData[1] = 0x20
        // perf counters (bytes 2-33): cycles=1000000 LE, instructions=500000 LE, rest 0
        mockData[2] = 0x40; mockData[3] = 0x42; mockData[4] = 0x0F; mockData[5] = 0x00
        mockData[6] = 0x00; mockData[7] = 0x00; mockData[8] = 0x00; mockData[9] = 0x00
        mockData[10] = 0x20; mockData[11] = 0xA1; mockData[12] = 0x07; mockData[13] = 0x00
    } else {
        mockData = []byte{byte(opcode), 0xAA, 0x55}
    }
    sm.handleResponse(mockData)
})
```

Note: `0x000F4240` = 1,000,000 and `0x0007A120` = 500,000 in little-endian.

- [ ] **Step 2: Update `CmdDumpState` handler in `ui.go`**

Find the `if cmd == CmdDumpState {` block. Replace it with:

```go
		// For DUMP_STATE, wait for 34-byte response (2 state bytes + 32 perf counter bytes)
		if cmd == CmdDumpState {
			time.Sleep(500 * time.Millisecond)

			responses := m.serialMgr.GetResponses()
			if len(responses) > 0 {
				lastResp := responses[len(responses)-1]
				if len(lastResp.Data) >= 34 {
					b0 := lastResp.Data[0]
					b1 := lastResp.Data[1]
					perf := lastResp.Data[2:34]

					dataMemStateNames := []string{
						"IDLE", "READ_SUBMITTING", "READ_AWAITING", "READ_SUCCESS",
						"WRITE_SUBMITTING", "WRITE_AWAITING", "WRITE_SUCCESS", "MEMORY_ERROR",
					}
					instrMemStateNames := []string{
						"IDLE", "READ_SUBMITTING", "READ_AWAITING", "READ_SUCCESS",
					}
					dataMemState := (b0 >> 5) & 0x7
					pipelineFlushed := (b0 >> 4) & 0x1
					stallS1 := (b0 >> 3) & 0x1
					enableFetch := (b0 >> 2) & 0x1
					s2Valid := (b0 >> 1) & 0x1
					s3Valid := b0 & 0x1
					instrMemState := (b1 >> 6) & 0x3
					initCalibComplete := (b1 >> 5) & 0x1

					cycles := uint64(perf[0]) | uint64(perf[1])<<8 | uint64(perf[2])<<16 | uint64(perf[3])<<24 |
						uint64(perf[4])<<32 | uint64(perf[5])<<40 | uint64(perf[6])<<48 | uint64(perf[7])<<56
					retired := uint32(perf[8]) | uint32(perf[9])<<8 | uint32(perf[10])<<16 | uint32(perf[11])<<24
					stallLoad := uint32(perf[12]) | uint32(perf[13])<<8 | uint32(perf[14])<<16 | uint32(perf[15])<<24
					stallStore := uint32(perf[16]) | uint32(perf[17])<<8 | uint32(perf[18])<<16 | uint32(perf[19])<<24
					stallFetch := uint32(perf[20]) | uint32(perf[21])<<8 | uint32(perf[22])<<16 | uint32(perf[23])<<24
					flushCycles := uint32(perf[24]) | uint32(perf[25])<<8 | uint32(perf[26])<<16 | uint32(perf[27])<<24
					memErrors := uint32(perf[28]) | uint32(perf[29])<<8 | uint32(perf[30])<<16 | uint32(perf[31])<<24

					var cpi float64
					if retired > 0 {
						cpi = float64(cycles) / float64(retired)
					}
					totalStall := uint64(stallLoad) + uint64(stallStore) + uint64(stallFetch) + uint64(flushCycles)
					var stallPct float64
					if cycles > 0 {
						stallPct = float64(totalStall) / float64(cycles) * 100
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
						float64(stallLoad)/float64(cycles)*100,
						float64(stallStore)/float64(cycles)*100,
						float64(stallFetch)/float64(cycles)*100,
						float64(flushCycles)/float64(cycles)*100,
						stallPct,
						memErrors,
					)
					return commandCompleteMsg{success: true, message: msg, cmd: cmd}
				}
			}

			return commandCompleteMsg{
				success: false,
				message: "Failed to read state dump (expected 34 bytes)",
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
git commit -m "feat: update DUMP_STATE Go handler to parse and display perf counters"
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

Select `[Mock Port - Testing Only]`, connect, navigate to `Dump State`, press Enter. Expected: 34-byte response parsed, CPI ~2.00 displayed (1,000,000 cycles / 500,000 instructions).
