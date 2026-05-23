# CPU Performance Counters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 8 hardware performance counters to the CPU, readable via a new `STATS_DUMP` debug command, with display in the Go debugger tool.

**Architecture:** Counters live in `cpu.v` as plain registers, gated on `i_Init_Calib_Complete`. They are packed into a 256-bit bus and wired to `debug_peripheral` as a new input. The peripheral gets a new opcode `0x0A` that streams the 32 bytes back over UART. The Go debugger parses and displays them.

**Tech Stack:** Verilog (SystemVerilog-compatible), Python/cocotb (tests), Go/bubbletea (debugger TUI)

---

## File Map

| File | Change |
|------|--------|
| `hdl/debug_peripheral/debug_peripheral.vh` | Add `op_STATS_DUMP = 8'h0A` |
| `hdl/debug_peripheral/debug_peripheral.v` | Add `i_Perf_Counters [255:0]` input port; add `op_STATS_DUMP` handler |
| `hdl/cpu/cpu.v` | Add 8 counter registers; wire packed bus; pass to `debug_peripheral` |
| `tests/cpu/constants.py` | Add `DEBUG_OP_STATS_DUMP = 0x0A` |
| `tests/cpu/integration_tests/test_perf_counters.py` | New: integration test for perf counters |
| `tools/debugger/opcodes.go` | Add `op_STATS_DUMP OpCode = 0x0A` and its `String()` case |
| `tools/debugger/commands.go` | Add `GetOpCode()` case for `CmdStatsDump`; mark `implemented: true` |
| `tools/debugger/stats.go` | New: `executeStatsDump()` and `formatStats()` |
| `tools/debugger/ui.go` | Wire `CmdStatsDump` into `executeCommand()` and `parseResponse()` |

---

## Task 1: Add opcode to hardware header and constants

**Files:**
- Modify: `hdl/debug_peripheral/debug_peripheral.vh`
- Modify: `tests/cpu/constants.py`

- [ ] **Step 1: Add opcode to `debug_peripheral.vh`**

In `hdl/debug_peripheral/debug_peripheral.vh`, add after the `op_WRITE_REGISTER` line:

```verilog
localparam op_STATS_DUMP = 8'h0A;
```

- [ ] **Step 2: Add opcode to Python constants**

In `tests/cpu/constants.py`, add after `DEBUG_OP_WRITE_REGISTER = 0x09`:

```python
DEBUG_OP_STATS_DUMP = 0x0A
```

- [ ] **Step 3: Verify existing tests still pass**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=integration
```

Expected: all existing integration tests pass (no behavioral change yet).

- [ ] **Step 4: Commit**

```bash
git add hdl/debug_peripheral/debug_peripheral.vh tests/cpu/constants.py
git commit -m "feat: add op_STATS_DUMP opcode constant (0x0A)"
```

---

## Task 2: Add performance counters to `cpu.v`

**Files:**
- Modify: `hdl/cpu/cpu.v`

All counter registers must be declared and incremented in `cpu.v`. The `w_S2_Is_Load` and `w_S2_Is_Store` wires already exist. `w_Stall_S1`, `w_Retire`, `w_Flush_Pipeline`, `r_Flushing_Pipeline`, `w_Instruction_Valid`, `w_Debug_Stall`, and `i_Init_Calib_Complete` are all already in scope.

- [ ] **Step 1: Declare counter registers**

Add after the `wire w_Retire = ...` line (around line 360):

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

Add a new `always @(posedge i_Clock)` block after the register declarations (before the `/*---DEBUG PERIPHERAL---*/` section):

```verilog
  always @(posedge i_Clock) begin
    if (w_Reset) begin
      r_Perf_Cycles                <= 64'd0;
      r_Perf_Instructions_Retired  <= 32'd0;
      r_Perf_Stall_Load            <= 32'd0;
      r_Perf_Stall_Store           <= 32'd0;
      r_Perf_Stall_Fetch           <= 32'd0;
      r_Perf_Flush_Cycles          <= 32'd0;
      r_Perf_Mem_Errors            <= 32'd0;
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

In the `debug_peripheral debug_peripheral (...)` instantiation (around line 376), add the new port connection:

```verilog
      .i_Perf_Counters(w_Perf_Counters),
```

- [ ] **Step 5: Verify existing tests still pass**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=integration
```

Expected: all existing integration tests pass (counters increment but nothing reads them yet).

- [ ] **Step 6: Commit**

```bash
git add hdl/cpu/cpu.v
git commit -m "feat: add performance counter registers to cpu.v"
```

---

## Task 3: Add `STATS_DUMP` handler to `debug_peripheral`

**Files:**
- Modify: `hdl/debug_peripheral/debug_peripheral.v`

The handler must send 32 bytes (bytes 0–31 of `i_Perf_Counters`) over UART, one byte per `r_Exec_Counter` tick, then transition to `s_IDLE`. The existing `op_READ_PC` handler (lines 139–160) uses the same pattern and is the reference.

- [ ] **Step 1: Add `i_Perf_Counters` input port**

In the module port list, add after `o_Write_PC_Data`:

```verilog
    input [255:0] i_Perf_Counters
```

- [ ] **Step 2: Add `op_STATS_DUMP` case**

In the `s_DECODE_AND_EXECUTE` case statement, add after the `op_WRITE_REGISTER` case and before `default`:

```verilog
            op_STATS_DUMP: begin
              if (r_Exec_Counter < 32) begin
                output_buffer[output_buffer_head] <= i_Perf_Counters[r_Exec_Counter*8 +: 8];
                output_buffer_head <= output_buffer_head + 1;
              end else begin
                r_State <= s_IDLE;
              end
            end
```

- [ ] **Step 3: Verify existing tests still pass**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=integration
```

Expected: all passing.

- [ ] **Step 4: Commit**

```bash
git add hdl/debug_peripheral/debug_peripheral.v
git commit -m "feat: add op_STATS_DUMP handler to debug_peripheral"
```

---

## Task 4: Write integration test for performance counters

**Files:**
- Create: `tests/cpu/integration_tests/test_perf_counters.py`

This test halts the CPU, fires `STATS_DUMP`, and verifies the 32-byte response is received. It then runs a known number of instructions and checks that `instructions_retired` increments correctly.

The test harness sets `i_Init_Calib_Complete = 1'b1` (see `cpu_integration_tests_harness.v` line 36), so counters will be active.

- [ ] **Step 1: Write the failing test**

Create `tests/cpu/integration_tests/test_perf_counters.py`:

```python
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

from cpu.utils import (
    gen_r_type_instruction,
    write_word_to_mem,
    uart_send_byte,
    wait_for_pipeline_flush,
)
from cpu.constants import (
    FUNC3_ALU_ADD_SUB,
    RAM_START_ADDR,
    DEBUG_OP_HALT,
    DEBUG_OP_UNHALT,
    DEBUG_OP_STATS_DUMP,
)

wait_ns = 1
STATS_RESPONSE_BYTES = 32


async def read_stats_dump(dut, clock):
    """Send STATS_DUMP and collect 32 bytes. Returns list of 32 ints."""
    await uart_send_byte(clock, dut.cpu.i_Uart_Tx_In,
                         dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV,
                         DEBUG_OP_STATS_DUMP)
    # Wait enough cycles for 32 bytes at 706 clocks/byte + margin
    await ClockCycles(clock, 706 * STATS_RESPONSE_BYTES + 500)

    # Collect output bytes from uart_transmitter output register
    # Read from output_buffer in debug_peripheral (simulation only)
    raw = []
    for i in range(STATS_RESPONSE_BYTES):
        raw.append(int(dut.cpu.debug_peripheral.output_buffer[i].value))
    return raw


def parse_u64_le(raw, offset):
    val = 0
    for i in range(8):
        val |= raw[offset + i] << (i * 8)
    return val


def parse_u32_le(raw, offset):
    val = 0
    for i in range(4):
        val |= raw[offset + i] << (i * 8)
    return val


@cocotb.test()
async def test_stats_dump_returns_32_bytes(dut):
    """STATS_DUMP handler sends exactly 32 bytes"""
    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 2)
    dut.i_Reset.value = 0
    await ClockCycles(dut.i_Clock, 2)

    await uart_send_byte(clock, dut.cpu.i_Uart_Tx_In,
                         dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV,
                         DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    raw = await read_stats_dump(dut, dut.i_Clock)
    assert len(raw) == STATS_RESPONSE_BYTES, \
        f"Expected 32 bytes, got {len(raw)}"


@cocotb.test()
async def test_instructions_retired_counts_correctly(dut):
    """instructions_retired increments once per retired instruction"""
    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 2)
    dut.i_Reset.value = 0

    # Read baseline retired count
    await uart_send_byte(clock, dut.cpu.i_Uart_Tx_In,
                         dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV,
                         DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)
    raw_before = await read_stats_dump(dut, dut.i_Clock)
    retired_before = parse_u32_le(raw_before, 8)

    # Write 3 ADD instructions followed by NOPs and run them
    start_address = RAM_START_ADDR
    add_instr = gen_r_type_instruction(3, FUNC3_ALU_ADD_SUB, 1, 2, 0)
    nop_instr = 0x00000013  # ADDI x0, x0, 0
    for i in range(3):
        write_word_to_mem(dut.instruction_ram.mem, start_address + i * 4, add_instr)
    for i in range(6):
        write_word_to_mem(dut.instruction_ram.mem, start_address + (3 + i) * 4, nop_instr)
    dut.cpu.r_PC.value = start_address

    await uart_send_byte(clock, dut.cpu.i_Uart_Tx_In,
                         dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV,
                         DEBUG_OP_UNHALT)
    # Run long enough for 3 instructions + pipeline drain
    await ClockCycles(dut.i_Clock, 30)

    await uart_send_byte(clock, dut.cpu.i_Uart_Tx_In,
                         dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV,
                         DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    raw_after = await read_stats_dump(dut, dut.i_Clock)
    retired_after = parse_u32_le(raw_after, 8)

    assert retired_after >= retired_before + 3, \
        f"Expected at least 3 more retired instructions, got {retired_after - retired_before}"


@cocotb.test()
async def test_cycles_advances(dut):
    """cycles counter increases over time"""
    clock = Clock(dut.i_Clock, wait_ns, "ns")
    cocotb.start_soon(clock.start())

    dut.i_Reset.value = 1
    await ClockCycles(dut.i_Clock, 2)
    dut.i_Reset.value = 0

    await uart_send_byte(clock, dut.cpu.i_Uart_Tx_In,
                         dut.cpu.debug_peripheral.uart_receiver.o_Rx_DV,
                         DEBUG_OP_HALT)
    await wait_for_pipeline_flush(dut)

    raw1 = await read_stats_dump(dut, dut.i_Clock)
    cycles1 = parse_u64_le(raw1, 0)

    await ClockCycles(dut.i_Clock, 100)

    raw2 = await read_stats_dump(dut, dut.i_Clock)
    cycles2 = parse_u64_le(raw2, 0)

    assert cycles2 > cycles1, \
        f"cycles did not advance: before={cycles1}, after={cycles2}"
```

- [ ] **Step 2: Run test to verify it fails (handler not wired yet)**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=integration TEST_FILE=test_perf_counters
```

Expected: FAIL — `DEBUG_OP_STATS_DUMP` not yet in constants, or response bytes are wrong.

- [ ] **Step 3: Run tests after full hardware implementation (Tasks 2 & 3 complete)**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=integration TEST_FILE=test_perf_counters
```

Expected: all 3 tests PASS.

- [ ] **Step 4: Run full test suite to check for regressions**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=all
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/cpu/integration_tests/test_perf_counters.py
git commit -m "test: add integration tests for perf counters"
```

---

## Task 5: Wire `CmdStatsDump` in Go debugger

**Files:**
- Modify: `tools/debugger/opcodes.go`
- Modify: `tools/debugger/commands.go`
- Create: `tools/debugger/stats.go`
- Modify: `tools/debugger/ui.go`

- [ ] **Step 1: Add opcode to `opcodes.go`**

Add to the const block after `op_WRITE_REGISTER`:

```go
op_STATS_DUMP OpCode = 0x0A
```

Add to the `String()` switch:

```go
case op_STATS_DUMP:
    return "STATS_DUMP"
```

- [ ] **Step 2: Wire `CmdStatsDump` in `commands.go`**

In `GetOpCode()`, add a case before `default`:

```go
case CmdStatsDump:
    return op_STATS_DUMP, true
```

Change the `CmdStatsDump` entry in `commands` map from `implemented: false` to `implemented: true`:

```go
CmdStatsDump: {"Read Stats", "Read CPU statistics", true},
```

- [ ] **Step 3: Create `tools/debugger/stats.go`**

```go
package main

import (
	"encoding/binary"
	"fmt"
	"time"
)

type PerfCounters struct {
	Cycles               uint64
	InstructionsRetired  uint32
	StallCyclesLoad      uint32
	StallCyclesStore     uint32
	StallCyclesFetch     uint32
	FlushCycles          uint32
	MemErrors            uint32
}

func parseStats(data []byte) (PerfCounters, error) {
	if len(data) < 32 {
		return PerfCounters{}, fmt.Errorf("expected 32 bytes, got %d", len(data))
	}
	return PerfCounters{
		Cycles:              binary.LittleEndian.Uint64(data[0:8]),
		InstructionsRetired: binary.LittleEndian.Uint32(data[8:12]),
		StallCyclesLoad:     binary.LittleEndian.Uint32(data[12:16]),
		StallCyclesStore:    binary.LittleEndian.Uint32(data[16:20]),
		StallCyclesFetch:    binary.LittleEndian.Uint32(data[20:24]),
		FlushCycles:         binary.LittleEndian.Uint32(data[24:28]),
		MemErrors:           binary.LittleEndian.Uint32(data[28:32]),
	}, nil
}

func formatStats(c PerfCounters) string {
	var cpi float64
	if c.InstructionsRetired > 0 {
		cpi = float64(c.Cycles) / float64(c.InstructionsRetired)
	}

	totalStall := uint64(c.StallCyclesLoad) + uint64(c.StallCyclesStore) +
		uint64(c.StallCyclesFetch) + uint64(c.FlushCycles)

	var stallPct float64
	if c.Cycles > 0 {
		stallPct = float64(totalStall) / float64(c.Cycles) * 100
	}

	return fmt.Sprintf(
		"CPU Performance Stats\n"+
			"─────────────────────────────────\n"+
			"  Cycles:              %d\n"+
			"  Instructions retired:%d\n"+
			"  CPI:                 %.2f\n"+
			"─────────────────────────────────\n"+
			"  Stall cycles (load): %d\n"+
			"  Stall cycles (store):%d\n"+
			"  Stall cycles (fetch):%d\n"+
			"  Flush cycles:        %d\n"+
			"  Total stall %%:       %.1f%%\n"+
			"─────────────────────────────────\n"+
			"  Memory errors:       %d\n",
		c.Cycles, c.InstructionsRetired, cpi,
		c.StallCyclesLoad, c.StallCyclesStore, c.StallCyclesFetch, c.FlushCycles,
		stallPct, c.MemErrors,
	)
}

func (m model) executeStatsDump() tea.Cmd {
	return func() tea.Msg {
		opcode, _ := CmdStatsDump.GetOpCode()
		err := m.serialMgr.SendCommand(opcode)
		if err != nil {
			return commandCompleteMsg{
				success: false,
				message: fmt.Sprintf("Failed to send STATS_DUMP: %v", err),
			}
		}

		time.Sleep(500 * time.Millisecond)

		responses := m.serialMgr.GetResponses()
		if len(responses) == 0 {
			return commandCompleteMsg{success: false, message: "No response from CPU"}
		}

		last := responses[len(responses)-1]
		counters, err := parseStats(last.Data)
		if err != nil {
			return commandCompleteMsg{
				success: false,
				message: fmt.Sprintf("Failed to parse stats: %v", err),
			}
		}

		return commandCompleteMsg{
			success: true,
			message: formatStats(counters),
			cmd:     CmdStatsDump,
		}
	}
}
```

Note: `stats.go` is in `package main` so it needs the `tea` import. Add `tea "github.com/charmbracelet/bubbletea"` to the imports in `stats.go`.

- [ ] **Step 4: Wire into `ui.go` `executeCommand()`**

In `executeCommand()` in `ui.go`, add a case before the final `time.Sleep` / default return:

```go
if cmd == CmdStatsDump {
    return m.executeStatsDump()
}
```

Add this block right after the `if cmd == CmdReadPC { ... }` block (around line 429).

- [ ] **Step 5: Add mock response for `op_STATS_DUMP` in `serial.go`**

In `SendCommand` mock branch in `serial.go`, the current code sends `[]byte{byte(opcode), 0xAA, 0x55}` for all commands. The stats response is 32 bytes. Update the mock to handle `op_STATS_DUMP`:

Find the `time.AfterFunc` block in `SendCommand` and replace it with:

```go
time.AfterFunc(50*time.Millisecond, func() {
    var mockData []byte
    if OpCode(opcode) == op_STATS_DUMP {
        mockData = make([]byte, 32)
        // cycles = 1000000, instructions = 500000, all others 0
        binary.LittleEndian.PutUint64(mockData[0:8], 1000000)
        binary.LittleEndian.PutUint32(mockData[8:12], 500000)
    } else {
        mockData = []byte{byte(opcode), 0xAA, 0x55}
    }
    sm.handleResponse(mockData)
})
```

Add `"encoding/binary"` to the imports in `serial.go`.

- [ ] **Step 6: Build and verify it compiles**

```bash
cd tools && go build ./debugger
```

Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add tools/debugger/opcodes.go tools/debugger/commands.go tools/debugger/stats.go tools/debugger/ui.go tools/debugger/serial.go
git commit -m "feat: implement CmdStatsDump in Go debugger"
```

---

## Task 6: Final verification

- [ ] **Step 1: Run full test suite**

```bash
cd tests && source test_env/bin/activate && make TEST_TYPE=all
```

Expected: all tests pass.

- [ ] **Step 2: Build debugger**

```bash
cd tools && go build ./debugger
```

Expected: clean build.

- [ ] **Step 3: Smoke test with mock port**

```bash
cd tools && go run ./debugger
```

Select `[Mock Port - Testing Only]`, navigate to `Read Stats`, press Enter. Expected: stats table displayed in the status area with CPI ~2.00 (1000000 cycles / 500000 instructions).

- [ ] **Step 4: Final commit if anything was tidied**

```bash
git add -p
git commit -m "chore: finalize perf counters implementation"
```
