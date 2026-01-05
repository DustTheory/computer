# MIG and Vivado Block Diagram Setup - WORKING CONFIGURATION

**Last updated**: 2026-01-04
**Status**: ✅ **MIG CALIBRATION SUCCESSFUL** - DDR3 functional, UART operational
**Source files**: Vivado project (not in repository), `hdl/reset_timer.v`
**Related docs**: [CLAUDE.md](../../CLAUDE.md), [memory-map.md](memory-map.md)

---

## Working MIG Configuration (Arty S7-50)

**Memory part**: MT41K128M16XX-15E (16-bit DDR3L, 128Mb, -15E speed grade, **1.35V operation**)
- **Data width**: 16 bits
- **Input clock**: **12 MHz** (pin F14) → Clock Wizard → **100 MHz sys_clk**, **200 MHz ref_clk**
- **Memory clock**: **324.99 MHz** (3077 ps, generated internally by MIG)
- **UI clock**: **81.25 MHz** (DDR3-650, 324.99 MHz ÷ 4 PHY ratio) - **CPU runs at this speed**
- **AXI interface**: 128-bit data width at MIG (SmartConnect handles width conversion from CPU's 32-bit)
- **I/O standard**: **SSTL135** (1.35V DDR3L compatible)

**Critical Success Factors**:
- ✅ 12 MHz input clock (pin F14, LVCMOS33)
- ✅ **200 MHz reference clock** to MIG `clk_ref_i` (MANDATORY for IDELAYCTRL calibration)
- ✅ Bank 34 for all DDR3 signals (SSTL135)
- ✅ CPU reset from `ui_clk_sync_rst` (not `peripheral_reset` which stays HIGH)

---

## MIG Configuration Details (Verified)

**Project Setup**:
- Target Device: `xc7s50-csga324` (Spartan-7 50, speed grade -1)
- Module Name: `computer_mig_7series_0_0`
- Selected Compatible Device: `xc7s25-csga324`

**MIG Controller Options**:
- Memory: DDR3_SDRAM
- Interface: AXI (128-bit data width, 28-bit address, 4-bit ID)
- **Input Clock Period: 10000 ps (100 MHz)** - this goes to sys_clk_i
- **Clock Period: 3077 ps (324.99 MHz)** - memory interface clock (MIG-generated)
- **Reference Clock: 200 MHz (5000 ps)** - MANDATORY for IDELAYCTRL
- Phy to Controller Clock Ratio: 4:1
- Memory Part: **MT41K128M16XX-15E** (16-bit, correct part)
- Data Width: 16 bits
- ECC: Disabled
- Arbitration Scheme: RD_PRI_REG
- **Resulting UI Clock: 81.25 MHz** (324.99 MHz ÷ 4)

**Bank Selection (WORKING CONFIGURATION)**:
- **Bank 34 ONLY** (all 4 byte groups):
  - Byte Group T0: DQ[0-7]
  - Byte Group T1: DQ[8-15]
  - Byte Group T2: Address/Ctrl-0
  - Byte Group T3: Address/Ctrl-1
- **I/O Standard**: SSTL135 (1.35V DDR3L)
- Bank 15: NOT USED (has RGB LEDs requiring 3.3V - incompatible with DDR3)

**Why this works**: Bank 34 is powered at 1.35V for DDR3L (all signals SSTL135). Bank 15 has RGB LEDs requiring 3.3V. Bank 14 is for UART (3.3V LVCMOS33). Separate banks = independent VCCO rails = no voltage conflict.

**FPGA Options**:
- System Clock Type: Single-Ended (NOT "No Buffer" as originally thought)
- Reference Clock Type: No Buffer
- System Clock Source: Pin R2 (note: actually fed from Clock Wizard internally)
- **Internal Vref: Enabled** (generates 0.675V for Bank 34 DDR3L I/O)
- Memory Voltage: **1.35V** (DDR3L)
- IO Power Reduction: ON
- DCI for DQ/DQS/DM: Enabled
- Internal Termination (HR Banks): 50 Ohms

---

## Reset Architecture

**Goal**: Hold MIG `sys_rst` (ACTIVE-LOW) for minimum 200µs during startup.

**Implementation**:
- Custom `hdl/reset_timer.v` module counts **20,000 cycles @ 100 MHz = 200µs**
- When Clock Wizard locks: timer starts
- During count: `o_Mig_Reset` = LOW (MIG held in reset)
- After count: `o_Mig_Reset` = HIGH (MIG reset released)
- Direct connection to MIG `sys_rst` (no inverter needed)
- **Parameters**: `COUNTER_WIDTH=15`, `HOLD_CYCLES=20000`


---

## Key Points for Claude - WORKING CONFIGURATION

**Clock Architecture**:
- Input: **12 MHz** (pin F14, LVCMOS33) from board oscillator
- Clock Wizard generates: **100 MHz** (sys_clk, reset_timer) and **200 MHz** (ref_clk - CRITICAL!)
- MIG generates: **324.99 MHz** internal memory clock, **81.25 MHz ui_clk** (CPU clock domain)

**Reset Architecture**:
- Reset timer: 20,000 cycles @ 100 MHz = 200µs hold time for MIG `sys_rst`
- **CPU reset**: Connected to `mig_7series_0/ui_clk_sync_rst` (ACTIVE-HIGH, synchronized to ui_clk)
- **NOT using `proc_sys_reset_0/peripheral_reset`** - that signal stays perpetually HIGH (known issue)

**Memory Configuration**:
- Part: MT41K128M16XX-15E (16-bit DDR3L, **1.35V operation**)
- I/O Standard: **SSTL135** (NOT SSTL15!)
- Bank: **Bank 34 only** (SSTL135)
- Internal Vref: 0.675V (half of 1.35V)

**Critical Requirements**:
- ✅ **200 MHz reference clock** to MIG `clk_ref_i` is MANDATORY - DDR3 will NOT calibrate without it
- ✅ Bank 34 with SSTL135 I/O standard (1.35V DDR3L)
- ✅ CPU clocked and reset from MIG's `ui_clk` and `ui_clk_sync_rst`
- ✅ AXI: MIG uses 128-bit width; SmartConnect handles CPU's 32-bit conversion

---

## Complete Vivado Block Diagram Setup

### Overview - WORKING CONFIGURATION

The design uses a modular Vivado block diagram with:
- **Input clock**: **12 MHz** from board oscillator (pin F14)
- **Clock Wizard**: Generates **100 MHz** (MIG sys_clk, reset_timer) and **200 MHz** (MIG ref_clk - CRITICAL!)
- **Reset conditioning**: Custom Verilog timer for MIG + Processor System Reset IP (unused for CPU)
- **Memory interface**: MIG 7-series DDR3L controller (generates 324.99 MHz internally, **81.25 MHz ui_clk**)
- **CPU**: Clocked by `ui_clk` (81.25 MHz), reset by `ui_clk_sync_rst` from MIG
- **CPU-to-Memory**: AXI SmartConnect bridges CPU dual masters to single MIG slave (128-bit)
- **Debug**: ILA cores for monitoring (clocked by 100 MHz system clock)

### Block Diagram Components (in signal flow order)

#### 1. Clock Input and External Reset
- **clk_in1_0**: **12 MHz** board oscillator (pin F14, Bank 15, LVCMOS33)
- **ext_reset_in_0**: External reset button (pin V14, Bank 14, LVCMOS33, ACTIVE-LOW)

#### 2. Clock Wizard (clk_wiz_0) - WORKING CONFIGURATION
**Purpose**: Generate 100 MHz for MIG system clock and 200 MHz reference clock from 12 MHz input

**Configuration**:
- Input: **12 MHz** from board (pin F14)
- Input Period: 83.333 ns (83333 ps)
- Primitive: MMCM (MMCME2_ADV)
- **CLKFBOUT_MULT_F**: 50 (VCO = 12 MHz × 50 = 600 MHz)
- **DIVCLK_DIVIDE**: 1
- Outputs:
  - `CLK_100`: 100 MHz (÷6) → MIG `sys_clk_i` AND reset_timer `i_Clock`
  - `CLK_200`: 200 MHz (÷3) → MIG `clk_ref_i` (**CRITICAL for IDELAYCTRL**)
  - `locked`: HIGH when MMCM locked → enables reset_timer

**Inputs**:
- `clk_in1`: 12 MHz oscillator (pin F14)
- `reset`: Active-high reset from NOT gate (inverted ext_reset_in_0)

**Connections**:
- `CLK_100` → `mig_7series_0/sys_clk_i`, `reset_timer_0/i_Clock`
- `CLK_200` → `mig_7series_0/clk_ref_i`
- `locked` → `reset_timer_0/i_Enable`, `proc_sys_reset_0/dcm_locked`

**Why these frequencies**: MIG generates 324.99 MHz internally (Clock Period 3077 ps) from the 100 MHz input. The **200 MHz reference clock is MANDATORY** for 7-series IDELAYCTRL calibration - DDR3 will NOT calibrate without it.

#### 3. Reset Conditioning Logic

**Util Vector Logic NOT Gate (util_vector_logic_0)**
- **Purpose**: Invert external reset from ACTIVE-LOW to ACTIVE-HIGH
- **Inputs**: `Op1` = ext_reset_in_0 (ACTIVE-LOW from button)
- **Output**: Active-HIGH reset to Clock Wizard and proc_sys_reset_0
- **Operation**: C_OPERATION="not", C_SIZE=1

**Custom Reset Timer (reset_timer_0)**
- **Type**: Custom Verilog module (`hdl/reset_timer.v`)
- **Purpose**: Hold MIG `sys_rst` LOW for 200µs during initialization
- **Parameters**:
  - `COUNTER_WIDTH`: **15 bits** (supports counts 0-32767)
  - `HOLD_CYCLES`: **20,000** (20000 × 10ns @ 100 MHz = 200µs)
- **Inputs**:
  - `i_Clock`: CLK_MIG_SYS (100 MHz)
  - `i_Enable`: clk_wiz_0/locked (starts counting when MMCM locks)
- **Output**:
  - `o_Mig_Reset`: ACTIVE-LOW to MIG `sys_rst`
  - Behavior: LOW during 0→20000 count, HIGH after 20000 (holds HIGH)
- **Direct connection** to MIG sys_rst (no inverter needed—already ACTIVE-LOW)

**Processor System Reset (proc_sys_reset_0)** - PARTIALLY USED
- **Purpose**: Generate synchronized AXI reset signals (NOT used for CPU reset)
- **Inputs**:
  - `ext_reset_in`: Active-HIGH reset from NOT gate
  - `slowest_sync_clk`: MIG `ui_clk` (81.25 MHz user interface clock)
  - `dcm_locked`: Clock Wizard `locked` signal
- **Outputs**:
  - `peripheral_aresetn`: Active-LOW reset → MIG `aresetn` (AXI reset)
  - `interconnect_aresetn`: Active-LOW reset → SmartConnect `aresetn`
  - `peripheral_reset`: **PERPETUALLY HIGH - NOT USED** (known issue)
- **Function**: Synchronizes AXI resets to ui_clk domain
- **Note**: `peripheral_reset` stays HIGH and cannot be used for CPU. CPU uses `ui_clk_sync_rst` instead.

#### 4. MIG 7-Series DDR3 Controller (mig_7series_0) - WORKING CONFIGURATION
**Purpose**: Interface CPU to external DDR3L memory - **✅ CALIBRATION SUCCESSFUL**

**Critical Configuration**:
- **Memory part**: MT41K128M16XX-15E (16-bit DDR3L, 128 Mb, -15E speed grade, **1.35V operation**)
- **Data width**: 16 bits
- **Bank selection**: **Bank 34 ONLY** (all DDR3, Bank 15 avoided due to RGB LED conflict)
- **Internal Vref**: **ENABLED** (generates 0.675V internal reference for Bank 34 SSTL135)
- **I/O Standard**: **SSTL135** (1.35V DDR3L compatible)
- **AXI interface**: 128-bit data, 28-bit address, 4-bit ID
- **Clock frequencies**:
  - `sys_clk_i`: **100 MHz** (10000 ps period, from Clock Wizard CLK_100)
  - `clk_ref_i`: **200 MHz** (5000 ps period, from Clock Wizard CLK_200) **← CRITICAL!**
  - Internal memory clock: **324.99 MHz** (3077 ps, MIG-generated)
  - `ui_clk`: **81.25 MHz** (Generated by MIG, 324.99 MHz ÷ 4 PHY ratio)

**Inputs**:
- `sys_clk_i`: **100 MHz** system clock from Clock Wizard
- `clk_ref_i`: **200 MHz** reference clock for IDELAYCTRL (**MANDATORY for calibration**)
- `sys_rst`: ACTIVE-LOW reset from reset_timer (minimum 200µs hold time)
- `aresetn`: ACTIVE-LOW AXI reset from proc_sys_reset_0/peripheral_aresetn
- `S_AXI`: AXI slave interface (128-bit) from SmartConnect

**Outputs**:
- `ui_clk`: **81.25 MHz** user interface clock (MIG-generated) → **CPU clock domain**
- `ui_clk_sync_rst`: ACTIVE-HIGH synchronous reset in ui_clk domain → **CPU reset**
- `init_calib_complete`: HIGH when calibration done (verified working)
- `mmcm_locked`: HIGH when internal MMCM locked
- `ddr3_*`: Physical DDR3 interface pins (address, data, control, DQS, etc.)

**DDR3 Pin Assignment**:
- **Bank 34, T0, T1, T2, T3** (ALL DDR3 signals, **SSTL135** 1.35V via Internal Vref 0.675V):
  - Address: ddr3_addr[13:0] (14 bits) - pins U2, R4, V2, V4, T3, R7, V6, T6, U7, V7, P6, T5, R6, U6
  - Bank select: ddr3_ba[2:0] (3 bits) - pins V5, T1, U3
  - Control: ddr3_ras_n (U1), ddr3_cas_n (V3), ddr3_we_n (P7), ddr3_cke[0] (T2), ddr3_cs_n[0] (R3), ddr3_odt[0] (P5)
  - Clock: ddr3_ck_p[0] (R5), ddr3_ck_n[0] (T4) - DIFF_SSTL135
  - Reset: ddr3_reset_n (J6) - SSTL135
  - Data: ddr3_dq[15:0] - pins K2, K3, L4, M6, K6, M4, L5, L6, N4, R1, N1, N5, M2, P1, M1, P2
  - Data strobes: ddr3_dqs_p[1:0] (K1, N3), ddr3_dqs_n[1:0] (L1, N2) - DIFF_SSTL135
  - Data mask: ddr3_dm[1:0] (K4, M3) - SSTL135
- **Bank 14**: UART at 3.3V LVCMOS33 (independent VCCO rail, no conflict)

#### 5. AXI SmartConnect (smartconnect_0)
**Purpose**: Bridge dual CPU masters to single MIG AXI slave

**Configuration**:
- Input ports:
  - `S00_AXI`: CPU data memory (32-bit)
  - `S01_AXI`: CPU instruction memory (32-bit)
- Output port:
  - `M00_AXI`: MIG DDR3 (32-bit, SmartConnect handles internal buffering/multiplexing)
- **Arbitration**: RD_PRI_REG (reads prioritized, registered arbitration)
- **Width conversion**: Automatic (SmartConnect buffers narrower transactions, combines into optimal MIG accesses)

**Inputs**:
- `aclk`: MIG `ui_clk` (all transactions synchronous to DDR3 clock)
- `aresetn`: ACTIVE-LOW reset from proc_sys_reset_0

#### 6. CPU Core (cpu) - WORKING CONFIGURATION
**Purpose**: RISC-V RV32I processor executing instructions from DDR3 - **✅ UART OPERATIONAL**

**Clock and Reset** (CRITICAL - this is what makes it work):
- `i_Clock`: MIG `ui_clk` (81.25 MHz, synchronized to DDR3 timing)
- `i_Reset`: **`ui_clk_sync_rst`** from MIG (ACTIVE-HIGH, synchronized to ui_clk)
  - **NOT** `proc_sys_reset_0/peripheral_reset` (that signal stays perpetually HIGH)

**Interfaces**:
- `i_Init_Calib_Complete`: MIG calibration status signal (goes HIGH when DDR3 ready)
- `s_instruction_memory_axil`: AXI-Lite master for instruction fetches (32-bit)
- `s_data_memory_axil`: AXI-Lite master for load/store operations (32-bit)
- `i_Uart_Tx_In`: UART transmit input (pin V12)
- `o_Uart_Rx_Out`: UART receive output (pin R12)

**Key properties**:
- Dual AXI-Lite masters (instruction and data buses) → SmartConnect → MIG (128-bit)
- CPU runs at 81.25 MHz ui_clk speed
- Debug peripheral operational with UART at 115200 baud
- Both masters connect to SmartConnect input ports
- Waits for `i_Init_Calib_Complete` HIGH before executing from DDR3

#### 7. UART Interface (Physical I/O)
**Purpose**: Serial communication to PC via USB

**Pins** (Bank 14, LVCMOS33, 3.3V):
- `i_Uart_Tx_In`: Pin V12 (FPGA input from USB-UART chip)
- `o_Uart_Rx_Out`: Pin R12 (FPGA output to USB-UART chip)

**Note**: Bank 15 (DDR3, 1.5V via Internal Vref) and Bank 14 (UART, 3.3V LVCMOS33) are separate banks with independent VCCO rails. No voltage conflict.

#### 8. Debug Infrastructure (ILA Cores)

**u_ila_0**: Reset and calibration monitoring
- **Clock**: `computer_i/mig_7series_0/u_computer_mig_7series_0_0_mig/u_ddr3_infrastructure/CLK` (MIG internal clock)
- **Probes**:
  - probe0: `init_calib_complete`
  - probe1: `mmcm_locked`
  - probe2: `peripheral_aresetn`
- **Purpose**: Monitor MIG initialization progress

**u_ila_1**: Reset timer monitoring
- **Clock**: `computer_i/clk_wiz_0/inst/CLK_200M_MIG` (200 MHz)
- **Probes**:
  - probe0: `reset_timer_0_o_Timer_Expired`
- **Purpose**: Verify reset timer reaches timeout

**u_ila_2**: (if configured) Additional debug points

### Signal Flow During Power-On - WORKING SEQUENCE

1. **T=0**: Power on, `ext_reset_in_0` = LOW (ACTIVE-LOW button pressed)
2. **T=~1ms**: User releases reset button, `ext_reset_in_0` = HIGH
3. **NOT gate inverts**: Output goes LOW → active-HIGH reset to Clock Wizard and proc_sys_reset_0
4. **Clock Wizard starts**: MMCM begins locking, using 12 MHz input
5. **T=~10ms**: Clock Wizard `locked` = HIGH, MMCM outputs **100 MHz** (CLK_100) and **200 MHz** (CLK_200)
6. **reset_timer starts**: `i_Enable` = HIGH (connected to `locked`), counter increments at **100 MHz**
7. **T=10ms to 10ms+200µs**: Counter counts 0→**20,000**, `o_Mig_Reset` = LOW
   - MIG `sys_rst` = LOW (held in reset)
   - MIG does not initialize while in reset
8. **T=10ms+200µs**: Counter reaches **20,000**, `o_Mig_Reset` = HIGH, stays HIGH
   - MIG `sys_rst` = HIGH (released from reset)
   - MIG starts DDR3L calibration using 100 MHz sys_clk and **200 MHz ref_clk**
   - **200 MHz ref_clk enables IDELAYCTRL calibration** (CRITICAL!)
9. **T=10ms+200µs+~300ms**: **MIG completes calibration successfully** ✅
   - `init_calib_complete` = HIGH (verified in ILA)
   - `ui_clk` stable and running at **81.25 MHz**
   - `mmcm_locked` = HIGH
   - `ui_clk_sync_rst` = LOW (CPU released from reset)
10. **proc_sys_reset_0**: Synchronizes, generates `peripheral_aresetn` and `interconnect_aresetn`
    - **NOTE**: `peripheral_reset` stays perpetually HIGH (known issue, not used)
11. **T=system ready**: CPU executes from DDR3, UART operational ✅

### XDC Constraints Summary - WORKING CONFIGURATION

**Clock pin**:
- `clk_in1_0`: Pin F14 (Bank 15, LVCMOS33) - 12 MHz oscillator input

**Reset pins**:
```
ext_reset_in_0: V14, LVCMOS33
```

**UART pins** (Bank 14):
```
i_Uart_Tx_In: V12, LVCMOS33
o_Uart_Rx_Out: R12, LVCMOS33
```

**DDR3 pins** (auto-generated by MIG in Bank 34):
```
Bank 34 (T0, T1, T2, T3) - ALL DDR3 signals at 1.35V (SSTL135 via Internal Vref 0.675V):
  ddr3_addr[13:0]: pins U2, R4, V2, V4, T3, R7, V6, T6, U7, V7, P6, T5, R6, U6
  ddr3_ba[2:0]: pins V5, T1, U3
  ddr3_ck_p[0]/ck_n[0]: pins R5/T4 - DIFF_SSTL135
  ddr3_ras_n, ddr3_cas_n, ddr3_we_n: pins U1, V3, P7
  ddr3_cke[0], ddr3_cs_n[0], ddr3_odt[0]: pins T2, R3, P5
  ddr3_reset_n: pin J6 - SSTL135
  ddr3_dq[15:0]: pins K2, K3, L4, M6, K6, M4, L5, L6, N4, R1, N1, N5, M2, P1, M1, P2
  ddr3_dqs_p[1:0]/dqs_n[1:0]: pins K1/L1, N3/N2 - DIFF_SSTL135
  ddr3_dm[1:0]: pins K4, M3 - SSTL135
```

**UART pins** (Bank 14 - independent VCCO 3.3V):
```
Bank 14 - UART at 3.3V (LVCMOS33):
  i_Uart_Tx_In: V12
  o_Uart_Rx_Out: R12
```

---

## Troubleshooting Log

**2026-01-02**: Root cause identified - MIG configured for wrong memory part (8-bit MT41J vs correct 16-bit MT41K). Also verified reset architecture is sound: custom timer provides required 200µs reset hold time to sys_rst.

**2026-01-03 (Part 1)**: Bank voltage conflict discovered - DRC error BIVC-1 when MIG mixed 3.3V UART (Bank 14 T3) with 1.5V DDR3 (Banks 14/15).

**2026-01-03 (Part 3)**: Debug peripheral investigation - confirmed that `i_Reset` (from `proc_sys_reset_0/peripheral_reset`) is stuck HIGH, preventing CPU operation. Debug peripheral only responds when its reset input is unconnected, indicating system reset is not being released. Root cause: MIG not completing initialization, or reset sequencing issue in block design. Need to verify:
- MIG `init_calib_complete` signal status via ILA
- `proc_sys_reset_0` reset release timing
- Reset timer `o_Mig_Reset` output
- Clock Wizard `locked` signal

**2026-01-03 (Part 4)**: ILA debugging confirmed:
- ✓ Clock Wizard locked = 1 (PLL stable)
- ✓ Reset timer `o_Mig_Reset` = 1 (proves 200 MHz clock running, 200µs reset hold completed)
- ✗ MIG `init_calib_complete` = 0 (calibration stuck/failed)

**Key insight**: Reset timer output = 1 proves the 200 MHz clock is working (counter reached 40,000 at 200 MHz). Issue is NOT clock-related.

**2026-01-03 (Part 5)**: **ROOT CAUSE CONFIRMED** - Clock configuration causes PLL VCO violation!

DRC error reveals the exact issue:
```
[DRC PDRC-43] PLL VCO frequency: 1800 MHz (exceeds Spartan-7 max of 1600 MHz)
Calculation: VCO = (3.333ns × 6) / 1 = 1800 MHz
CLKIN1_PERIOD = 3.333ns (300 MHz sys_clk actual input)
```

**Root cause:** MIG configured for "Input Clock Period: 3300ps (303 MHz)" but:
1. Actual sys_clk is 300 MHz (from Clock Wizard)
2. MIG also expects 303 MHz on clk_ref_i but receives 200 MHz
3. PLL multiply factor (×6) designed for 303 MHz pushes VCO to 1800 MHz with 300 MHz input
4. Spartan-7 PLL VCO max is 1600 MHz → DRC error → synthesis may continue but calibration fails

**Fix (Option A - Recommended, proven working):**
1. Reconfigure MIG: "Input Clock Period" = **10000ps (100 MHz)**
2. Reconfigure Clock Wizard: Change 200 MHz output to **100 MHz**
3. Update reset_timer: `HOLD_CYCLES = 20000` (200µs @ 100 MHz)
4. Result: Matches Element14 working example, Vivado selects PLL parameters that keep VCO ≤ 1600 MHz

**Fix (Option B - Quick test):**
1. Reconfigure MIG: "Input Clock Period" = **5000ps (200 MHz)** (match actual Clock Wizard output)
2. Keep Clock Wizard at 300 MHz + 200 MHz
3. Let Vivado recalculate PLL parameters for 200 MHz ref_clk
4. Check if DRC error clears (different PLL ratios may stay under VCO limit)

**2026-01-04**: **ACTUAL WORKING CONFIGURATION** - Clock frequency and bank selection resolved.

**Problem 1 - Clock Frequency**:
- Initial attempt: 300 MHz sys_clk (3333 ps period) was OUTSIDE MIG's allowed range (3000-3300 ps)
- MIG wizard system clock period constraint: **3000-3300 ps** (303-333 MHz)
- 300 MHz = 3333 ps → rejected by MIG

**Solution 1**:
1. **Clock Wizard configuration**:
   - Generate **320 MHz** from 100 MHz (within MIG's 3000-3300 ps range)
   - Use **same 320 MHz** for both sys_clk and ref_clk (simplifies design, avoids VCO violations)
2. **MIG configuration**:
   - System Clock Period: **3125 ps** (within 3000-3300 range ✓)
   - Reference Clock Period: **3124 ps** (same clock)
3. **Reset timer update**:
   - COUNTER_WIDTH: **17** (supports up to 131071)
   - HOLD_CYCLES: **64,000** (320 MHz × 200µs)

**Problem 2 - Bank Selection (CRITICAL)**:
- **Bank 15 has RGB LEDs** requiring 3.3V LVCMOS33
- DDR3 requires 1.35V SSTL135 with Internal Vref
- **CANNOT mix 3.3V and 1.35V I/O standards on same bank** - VCCO voltage conflict
- This caused MIG calibration to never complete

**Solution 2**:
- **Use Bank 34 for ALL DDR3 signals** (data, address, control)
- Bank 34 has no 3.3V peripherals - can be powered at 1.35V for DDR3L
- Bank 15 left unused (or available for 3.3V signals only)

**Problem 3 - Missing 200 MHz Reference Clock (CRITICAL)**:
- Initial attempts used same clock for sys_clk and clk_ref_i (100 MHz or 320 MHz both)
- **7-series MIG REQUIRES 200 MHz reference clock** for IDELAYCTRL calibration
- Without 200 MHz ref_clk, DDR3 calibration will NEVER complete

**Solution 3**:
- Switch input clock from 100 MHz (pin R2) to **12 MHz (pin F14)**
- Clock Wizard generates: 100 MHz (sys_clk) and **200 MHz (ref_clk)**
- Connect CLK_200 to MIG `clk_ref_i`
- Result: **init_calib_complete goes HIGH** ✅

**Problem 4 - proc_sys_reset_0 peripheral_reset Perpetually HIGH (KNOWN ISSUE)**:
- `proc_sys_reset_0/peripheral_reset` stays perpetually HIGH
- Cannot be used for CPU reset
- Root cause: Unknown (likely misconfiguration or timing issue in proc_sys_reset_0)

**Solution 4 (WORKAROUND)**:
- **Use `ui_clk_sync_rst` from MIG directly** for CPU reset
- This is ACTIVE-HIGH, synchronized to ui_clk (81.25 MHz)
- Goes LOW after MIG calibration completes
- Result: **CPU and UART operational** ✅

---

**2026-01-04 FINAL**: **✅ WORKING CONFIGURATION ACHIEVED**

**Summary of working setup**:
- Input: 12 MHz clock (pin F14, LVCMOS33)
- Clock Wizard: 100 MHz + 200 MHz outputs
- MIG: 100 MHz sys_clk, 200 MHz ref_clk (CRITICAL), DDR3L 1.35V on Bank 34 (SSTL135)
- CPU: Clocked by ui_clk (81.25 MHz), reset by ui_clk_sync_rst
- Result: MIG calibration successful, DDR3 operational, UART working

**Known Issue** (to be investigated):
- `proc_sys_reset_0/peripheral_reset` stays perpetually HIGH
- Currently using `ui_clk_sync_rst` as workaround for CPU reset
- Future: Investigate why peripheral_reset doesn't release (possibly aux_reset_in or slowest_sync_clk misconfiguration)

**Key Lessons Learned**:
1. **200 MHz reference clock is MANDATORY** for 7-series DDR3 IDELAYCTRL - non-negotiable
2. **Bank selection CRITICAL** - cannot mix I/O voltage standards (3.3V vs 1.35V) on same bank
3. **I/O standard matters**: Use SSTL135 for DDR3L (1.35V), not SSTL15 (1.5V)
4. Check board schematic for ALL peripherals on selected banks before configuring MIG
5. Use MIG's `ui_clk_sync_rst` if `proc_sys_reset_0` misbehaves

---
