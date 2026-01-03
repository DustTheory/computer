# AXI Interface

**Last updated**: 2026-01-02  
**Source files**: `hdl/cpu/memory/memory_axi.v`, `hdl/cpu/memory/memory.vh`  
**Related docs**: [memory-map.md](memory-map.md), [cpu-architecture.md](cpu-architecture.md)

---

AXI4-Lite memory bus implementation for CPU instruction/data access.

## Overview

**Protocol**: AXI4-Lite (simplified AXI4, no burst transfers)

**Module**: `hdl/cpu/memory/memory_axi.v`

**Purpose**: Interface between CPU and memory (BRAM ROM + DDR3 RAM). Handles load/store operations with byte/half/word granularity.

**Address space**:
- ROM: 0x0 - 0xFFF (4KB BRAM)
- RAM: 0x1000+ (DDR3 via Xilinx MIG)

## AXI4-Lite Signal Groups

### Read Address Channel (AR)
- `s_axil_araddr[31:0]` - Read address
- `s_axil_arvalid` - Address valid (master asserts)
- `s_axil_arready` - Address accepted (slave asserts)

### Read Data Channel (R)
- `s_axil_rdata[31:0]` - Read data
- `s_axil_rvalid` - Data valid (slave asserts)
- `s_axil_rready` - Ready to accept data (master asserts)

### Write Address Channel (AW)
- `s_axil_awaddr[31:0]` - Write address
- `s_axil_awvalid` - Address valid (master asserts)
- `s_axil_awready` - Address accepted (slave asserts)

### Write Data Channel (W)
- `s_axil_wdata[31:0]` - Write data
- `s_axil_wstrb[3:0]` - Write strobes (byte enables)
- `s_axil_wvalid` - Data valid (master asserts)
- `s_axil_wready` - Ready to accept data (slave asserts)

### Write Response Channel (B)
- `s_axil_bresp[1:0]` - Write response (unbound in current design)
- `s_axil_bvalid` - Response valid (slave asserts)
- `s_axil_bready` - Ready to accept response (master asserts)

## State Machine

**States** (from `memory.vh`):
```verilog
IDLE              = 3'd0
READ_SUBMITTING   = 3'd1
READ_AWAITING     = 3'd2
READ_SUCCESS      = 3'd3
WRITE_SUBMITTING  = 3'd4
WRITE_AWAITING    = 3'd5
WRITE_SUCCESS     = 3'd6
```

### Read Transaction Flow

1. **IDLE**: Module waits for `i_Enable` and load instruction (`LS_TYPE_LOAD_*`)
2. **READ_SUBMITTING**: 
   - Assert `s_axil_arvalid = 1`
   - Drive `s_axil_araddr = i_Addr`
   - Wait for `s_axil_arready` (slave accepts address)
3. **READ_AWAITING**: 
   - Assert `s_axil_rready = 1`
   - Wait for `s_axil_rvalid` (slave provides data)
4. **READ_SUCCESS**: 
   - Capture `s_axil_rdata`
   - Extract byte/half/word based on `i_Load_Store_Type` and `i_Addr[1:0]`
   - Return to IDLE next cycle

**Timing**: Minimum 2 cycles (submit + await), typical 3-4 cycles depending on memory latency

### Write Transaction Flow

1. **IDLE**: Module waits for `i_Enable`, `i_Write_Enable`, and store instruction (`LS_TYPE_STORE_*`)
2. **WRITE_SUBMITTING**: 
   - Assert `s_axil_awvalid = 1`, `s_axil_wvalid = 1`
   - Drive `s_axil_awaddr = i_Addr`
   - Drive `s_axil_wdata = w_Prepared_WData` (byte-aligned)
   - Drive `s_axil_wstrb = w_Prepared_WStrb` (byte enables)
   - Wait for `s_axil_awready` AND `s_axil_wready`
   - If `s_axil_bvalid` already high, go directly to WRITE_SUCCESS, else go to WRITE_AWAITING
3. **WRITE_AWAITING**: 
   - Assert `s_axil_bready = 1`
   - Wait for `s_axil_bvalid` (slave acknowledges write completion)
4. **WRITE_SUCCESS**: 
   - Return to IDLE next cycle

**Timing**: Minimum 2 cycles (submit + await), typical 3-4 cycles

## Byte/Half/Word Handling

### Store Data Preparation

**Byte offset**: `i_Addr[1:0]` determines where to place data within 32-bit word.

**Logic** (combinational, in `always @*` block):

#### Store Word (SW)
- `w_Prepared_WData = i_Data` (full 32 bits)
- `w_Prepared_WStrb = 4'b1111` (all bytes enabled)

#### Store Half (SH)
- **Offset 0 (i_Addr[1]=0)**: `{16'b0, i_Data[15:0]}`, strobe `4'b0011`
- **Offset 2 (i_Addr[1]=1)**: `{i_Data[15:0], 16'b0}`, strobe `4'b1100`

#### Store Byte (SB)
- **Offset 0**: `{24'b0, i_Data[7:0]}`, strobe `4'b0001`
- **Offset 1**: `{16'b0, i_Data[7:0], 8'b0}`, strobe `4'b0010`
- **Offset 2**: `{8'b0, i_Data[7:0], 16'b0}`, strobe `4'b0100`
- **Offset 3**: `{i_Data[7:0], 24'b0}`, strobe `4'b1000`

**Key insight**: AXI write strobes (`wstrb`) enable byte-level writes. CPU doesn't need read-modify-write for sub-word stores.

### Load Data Extraction

**Logic** (combinational, in `always @*` block):

#### Load Word (LW)
- `o_Data = s_axil_rdata` (full 32 bits)

#### Load Half (LH, signed)
- **Offset 0**: `{{16{s_axil_rdata[15]}}, s_axil_rdata[15:0]}` (sign-extend)
- **Offset 2**: `{{16{s_axil_rdata[31]}}, s_axil_rdata[31:16]}` (sign-extend)

#### Load Half Unsigned (LHU)
- **Offset 0**: `{16'b0, s_axil_rdata[15:0]}`
- **Offset 2**: `{16'b0, s_axil_rdata[31:16]}`

#### Load Byte (LB, signed)
- **Offset 0**: `{{24{s_axil_rdata[7]}}, s_axil_rdata[7:0]}` (sign-extend)
- **Offset 1**: `{{24{s_axil_rdata[15]}}, s_axil_rdata[15:8]}` (sign-extend)
- **Offset 2**: `{{24{s_axil_rdata[23]}}, s_axil_rdata[23:16]}` (sign-extend)
- **Offset 3**: `{{24{s_axil_rdata[31]}}, s_axil_rdata[31:24]}` (sign-extend)

#### Load Byte Unsigned (LBU)
- **Offset 0**: `{24'b0, s_axil_rdata[7:0]}`
- **Offset 1**: `{24'b0, s_axil_rdata[15:8]}`
- **Offset 2**: `{24'b0, s_axil_rdata[23:16]}`
- **Offset 3**: `{24'b0, s_axil_rdata[31:24]}`

## Signal Assignments

**Combinational outputs** (driven by state):

```verilog
s_axil_araddr  = (r_State == READ_SUBMITTING)  ? i_Addr : 0;
s_axil_arvalid = (r_State == READ_SUBMITTING);
s_axil_rready  = (r_State == READ_AWAITING);

s_axil_awvalid = (r_State == WRITE_SUBMITTING);
s_axil_awaddr  = (r_State == WRITE_SUBMITTING) ? i_Addr : 0;
s_axil_wvalid  = (r_State == WRITE_SUBMITTING);
s_axil_wdata   = (r_State == WRITE_SUBMITTING) ? w_Prepared_WData : 0;
s_axil_wstrb   = (r_State == WRITE_SUBMITTING) ? w_Prepared_WStrb : 0;
s_axil_bready  = (r_State == WRITE_SUBMITTING);
```

**Pattern**: Signals only driven when in relevant state, otherwise 0.

## Load/Store Types

**From `memory.vh`**:
```verilog
LS_TYPE_LOAD_WORD            = 4'b0000
LS_TYPE_LOAD_HALF            = 4'b0001
LS_TYPE_LOAD_HALF_UNSIGNED   = 4'b0010
LS_TYPE_LOAD_BYTE            = 4'b0011
LS_TYPE_LOAD_BYTE_UNSIGNED   = 4'b0100
LS_TYPE_STORE_WORD           = 4'b1000
LS_TYPE_STORE_HALF           = 4'b1001
LS_TYPE_STORE_BYTE           = 4'b1010
```

**MSB distinguishes load (0) vs store (1)**.

## Usage in CPU

**Module instantiation** (in `cpu.v`):
```verilog
memory_axi mem_axi (
    .i_Reset(i_Reset),
    .i_Clock(i_Clock),
    .i_Enable(w_Memory_Enable),
    .i_Write_Enable(w_Memory_Write_Enable),
    .i_Load_Store_Type(w_Load_Store_Type),
    .i_Addr(w_Memory_Address),
    .i_Data(w_Memory_Write_Data),
    .o_Data(w_Memory_Read_Data),
    .o_State(w_Memory_State),
    // AXI ports connected to MIG or BRAM controller...
);
```

**Control flow**:
1. CPU Stage 1 generates `w_Memory_Address`, `w_Load_Store_Type`, `w_Memory_Write_Data`
2. Stage 2 asserts `w_Memory_Enable` (and `w_Memory_Write_Enable` for stores)
3. `memory_axi` executes transaction over 2-4 cycles
4. CPU waits in Stage 2 until `w_Memory_State == IDLE` (transaction complete)
5. Stage 3 receives `w_Memory_Read_Data` for loads

## Testing

**File**: `tests/cpu/unit_tests/test_memory_axi.py`

**Pattern**:
```python
# Setup
dut.i_Enable.value = 1
dut.i_Write_Enable.value = 0
dut.i_Load_Store_Type.value = LS_TYPE_LOAD_WORD
dut.i_Addr.value = 0x1004

# Mock AXI slave
if dut.s_axil_arvalid.value:
    dut.s_axil_arready.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.s_axil_arready.value = 0
    dut.s_axil_rdata.value = 0xDEADBEEF
    dut.s_axil_rvalid.value = 1
    await ClockCycles(dut.i_Clock, 1)
    dut.s_axil_rvalid.value = 0

# Check result
assert dut.o_Data.value == 0xDEADBEEF
assert dut.o_State.value == IDLE
```

**Integration tests**: Use `axil_ram` test fixture from `hdl_inc/axil_ram.v` to simulate AXI memory.

## Known Issues

**⚠ No error handling**: `s_axil_bresp` is marked "Unbound to anything for now, used just for testing". Write errors not detected or handled.

**⚠ No timeout**: If AXI slave hangs (e.g., MIG calibration fails), state machine stalls forever. CPU freezes.

**⚠ No alignment check**: Module accepts misaligned addresses (e.g., LW from 0x1001). Behavior undefined by RISC-V spec. Should raise misaligned exception.

**⚠ Simultaneous AW/W assertion**: Write channel sends address and data together. Works for simple slaves but may fail for pipelined AXI.

## Waveform Example

**Load Word from 0x1000**:
```
Cycle | State            | araddr | arvalid | arready | rdata      | rvalid | rready | o_Data
------|------------------|--------|---------|---------|------------|--------|--------|--------
  1   | IDLE             | 0      | 0       | 0       | X          | 0      | 0      | 0
  2   | READ_SUBMITTING  | 0x1000 | 1       | 0       | X          | 0      | 0      | 0
  3   | READ_SUBMITTING  | 0x1000 | 1       | 1       | X          | 0      | 0      | 0
  4   | READ_AWAITING    | 0      | 0       | 0       | 0x12345678 | 1      | 1      | 0x12345678
  5   | READ_SUCCESS     | 0      | 0       | 0       | X          | 0      | 0      | 0x12345678
  6   | IDLE             | 0      | 0       | 0       | X          | 0      | 0      | 0x12345678
```

**Store Byte to 0x1002 (offset 2)**:
```
Cycle | State            | awaddr | awvalid | awready | wdata      | wstrb  | wvalid | wready | bvalid | bready
------|------------------|--------|---------|---------|------------|--------|--------|--------|--------|-------
  1   | IDLE             | 0      | 0       | 0       | 0          | 0      | 0      | 0      | 0      | 0
  2   | WRITE_SUBMITTING | 0x1002 | 1       | 0       | 0x00AB0000 | 0b0100 | 1      | 0      | 0      | 1
  3   | WRITE_SUBMITTING | 0x1002 | 1       | 1       | 0x00AB0000 | 0b0100 | 1      | 1      | 0      | 1
  4   | WRITE_AWAITING   | 0      | 0       | 0       | 0          | 0      | 0      | 0      | 1      | 1
  5   | WRITE_SUCCESS    | 0      | 0       | 0       | 0          | 0      | 0      | 0      | 0      | 0
  6   | IDLE             | 0      | 0       | 0       | 0          | 0      | 0      | 0      | 0      | 0
```

## Future Enhancements

**Add error detection**:
1. Check `s_axil_bresp` after writes (0b00 = OKAY, 0b10 = SLVERR)
2. Add timeout counter for stalled transactions
3. Raise CPU exception on memory error

**Add alignment check**:
1. Detect misaligned access: `(i_Addr[1:0] != 0) && (LS_TYPE == LOAD/STORE_WORD)`
2. Raise misaligned address exception

**Pipelined writes**:
1. Separate AW and W channels (allow address before data ready)
2. Add FIFO for write data buffering
