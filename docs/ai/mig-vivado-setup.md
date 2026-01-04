# MIG and Vivado Block Diagram Setup

**Last updated**: 2026-01-04
**Source files**: Vivado project (not in repository), `hdl/reset_timer.v`
**Related docs**: [CLAUDE.md](../../CLAUDE.md), [memory-map.md](memory-map.md)

---

## MIG Configuration (Arty S7-50)

**Memory part**: MT41K128M16XX-15E (16-bit DDR3, 128Mb, -15E speed grade)
- **Data width**: 16 bits
- **Clock**: 100 MHz input → Clock Wizard → **320 MHz sys_clk (3125 ps)**, **320 MHz ref_clk (3124 ps)**
- **UI clock**: **80 MHz** (DDR3-640, 320 MHz ÷ 4 PHY ratio)
- **AXI interface**: 128-bit data width at MIG (SmartConnect handles width conversion from CPU's 32-bit)

**Critical**: Ensure MIG configured for **MT41K128M16XX-15E**, NOT MT41J128M8XX-125 (8-bit). **Use Bank 34 ONLY** (Bank 15 has RGB LEDs causing voltage conflict).

---

## MIG Configuration Details (Verified)

**Project Setup**:
- Target Device: `xc7s50-csga324` (Spartan-7 50, speed grade -1)
- Module Name: `computer_mig_7series_0_0`
- Selected Compatible Device: `xc7s25-csga324`

**MIG Controller Options**:
- Memory: DDR3_SDRAM
- Interface: AXI (128-bit data width, 28-bit address, 4-bit ID)
- **System Clock Period: 3125 ps (320 MHz)**
- **Reference Clock Period: 3124 ps (320 MHz)**
- Phy to Controller Clock Ratio: 4:1
- Memory Part: **MT41K128M16XX-15E** (16-bit, correct part)
- Data Width: 16 bits
- ECC: Disabled
- Arbitration Scheme: RD_PRI_REG
- **Resulting UI Clock: 80 MHz** (320 MHz ÷ 4)

**Bank Selection (ACTUAL WORKING CONFIGURATION)**:
- **Bank 34 ONLY** (all 4 byte groups):
  - Byte Group T0: DQ[0-7]
  - Byte Group T1: DQ[8-15]
  - Byte Group T2: Address/Ctrl-0
  - Byte Group T3: Address/Ctrl-1
- **Bank 15**: Listed in config but has NO DDR3 pins assigned (avoid due to RGB LED voltage conflict)

**Why this works**: Bank 34 is dedicated entirely to DDR3 (all signals 1.5V SSTL135). Bank 15 has RGB LEDs requiring 3.3V, so it CANNOT be used for DDR3. Bank 14 is for UART (3.3V LVCMOS33). Separate banks = independent VCCO rails = no voltage conflict.

**FPGA Options**:
- System Clock Type: No Buffer
- Reference Clock Type: No Buffer
- **Internal Vref: Enabled** (generates 1.5V for Bank 15 DDR3 I/O)
- IO Power Reduction: ON
- DCI for DQ/DQS/DM: Enabled
- Internal Termination (HR Banks): 50 Ohms

---

## Reset Architecture

**Goal**: Hold MIG `sys_rst` (ACTIVE-LOW) for minimum 200µs during startup.

**Implementation**:
- Custom `hdl/reset_timer.v` module counts **64,000 cycles @ 320 MHz = 200µs**
- When Clock Wizard locks: timer starts
- During count: `o_Mig_Reset` = LOW (MIG held in reset)
- After count: `o_Mig_Reset` = HIGH (MIG reset released)
- Direct connection to MIG `sys_rst` (no inverter needed)
- **Parameters**: `COUNTER_WIDTH=17`, `HOLD_CYCLES=64000`


---

## Key Points for Claude

- **⚠️ CRITICAL: NEVER modify `/home/emma/gpu/config/arty-s7-50.xdc`** - This file is USER/VIVADO-CONTROLLED ONLY. Only user or Vivado GUI can make changes to it. If XDC changes are needed, provide guidance only; do not edit directly.
- **Reset timer**: Custom `hdl/reset_timer.v` provides 200µs hold time (64,000 cycles @ 320 MHz) for MIG sys_rst
- **Memory part**: Verify MIG is configured for MT41K128M16XX-15E (16-bit), not MT41J128M8XX-125 (8-bit)
- **Clock frequencies**: **320 MHz sys_clk (3125 ps)** and **320 MHz ref_clk (3124 ps)** from Clock Wizard
- **UI clock**: MIG generates **80 MHz ui_clk** (320 MHz ÷ 4 PHY ratio) - CPU runs at this speed
- **Signal polarity**: MIG `sys_rst` is ACTIVE-LOW (LOW=reset, HIGH=normal)
- **AXI**: MIG uses 128-bit AXI data width; SmartConnect handles width conversion from CPU's 32-bit AXI-Lite
- **Bank assignment**: **MUST use Bank 34 for DDR3** - Bank 15 has RGB LEDs (3.3V) incompatible with DDR3 (1.5V)

---

## Complete Vivado Block Diagram Setup

### Overview
The design uses a modular Vivado block diagram with:
- **Input clock**: 100 MHz from board oscillator
- **Clock Wizard**: Generates **320 MHz** (MIG sys_clk and ref_clk, reset_timer clock)
- **Reset conditioning**: Custom Verilog timer + Processor System Reset IP
- **Memory interface**: MIG 7-series DDR3 controller
- **CPU-to-Memory**: AXI SmartConnect bridges CPU dual masters to single MIG slave
- **Debug**: ILA cores for reset and calibration signal monitoring

### Block Diagram Components (in signal flow order)

#### 1. Clock Input and External Reset
- **clk_in1_0**: 100 MHz board oscillator (pin R2, Bank 34, LVCMOS33)
- **ext_reset_in_0**: External reset button (pin V14, Bank 14, LVCMOS33, ACTIVE-LOW)

#### 2. Clock Wizard (clk_wiz_0)
**Purpose**: Generate stable 320 MHz clock for MIG system, reference, and reset timer

**Configuration**:
- Input: 100 MHz from board
- Primitive: PLL (PLLE2_ADV)
- **CLKFBOUT_MULT_F**: 32 (VCO = 100 MHz × 32 = 3200 MHz) OR **CLKFBOUT_MULT**: 4, **DIVCLK_DIVIDE**: 1 (VCO = 100 MHz × 4 / 1 = 400 MHz with different multiplier internally)
- Outputs:
  - `CLK_320M_MIG`: 320 MHz → MIG `sys_clk_i`, MIG `clk_ref_i`, AND reset_timer clock
  - `locked`: HIGH when PLL locked → enables reset_timer

**Inputs**:
- `clk_in1`: 100 MHz oscillator
- `reset`: Active-high reset from NOT gate (inverted ext_reset_in_0)

**Why this frequency**: MIG system clock must be 3000-3300 ps (303-333 MHz). 320 MHz (3125 ps) is within range. Using same clock for sys_clk and ref_clk simplifies design and avoids PLL VCO limit violations.

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
  - `COUNTER_WIDTH`: **17 bits** (supports counts 0-131071)
  - `HOLD_CYCLES`: **64,000** (64000 × 3.125ns @ 320 MHz = 200µs)
- **Inputs**:
  - `i_Clock`: CLK_320M_MIG (320 MHz)
  - `i_Enable`: clk_wiz_0/locked (starts counting when PLL locks)
- **Output**:
  - `o_Mig_Reset`: ACTIVE-LOW to MIG `sys_rst`
  - Behavior: LOW during 0→64000 count, HIGH after 64000 (holds HIGH)
- **Direct connection** to MIG sys_rst (no inverter needed—already ACTIVE-LOW)

**Processor System Reset (proc_sys_reset_0)**
- **Purpose**: Generate synchronized AXI reset signals for system
- **Inputs**:
  - `ext_reset_in`: Active-HIGH reset from NOT gate
  - `slowest_sync_clk`: MIG `ui_clk` (user interface clock)
  - `dcm_locked`: Clock Wizard `locked` signal
- **Outputs**:
  - `peripheral_aresetn`: Active-LOW reset to MIG AXI aresetn
  - `interconnect_aresetn`: Active-LOW reset to SmartConnect
  - `peripheral_reset`: Active-HIGH reset to CPU
- **Function**: Synchronizes external reset to ui_clk domain, waits for Clock Wizard lock

#### 4. MIG 7-Series DDR3 Controller (mig_7series_0)
**Purpose**: Interface CPU to external DDR3 memory

**Critical Configuration**:
- **Memory part**: MT41K128M16XX-15E (16-bit DDR3, 128 Mb, -15E speed grade)
- **Data width**: 16 bits
- **Bank selection**: **Bank 34 ONLY** (all DDR3, Bank 15 avoided due to RGB LED conflict)
- **Internal Vref**: **ENABLED** (generates 1.5V internal reference for Bank 34)
- **AXI interface**: 128-bit data, 28-bit address, 4-bit ID
- **Clock frequencies**:
  - `sys_clk_i`: **320 MHz** (3125 ps period, from Clock Wizard)
  - `clk_ref_i`: **320 MHz** (3124 ps period, from Clock Wizard, MMCM timing reference)
  - `ui_clk`: **80 MHz** (Generated by MIG, 320 MHz ÷ 4 PHY ratio)

**Inputs**:
- `sys_clk_i`: **320 MHz** system clock
- `clk_ref_i`: **320 MHz** reference clock for MMCM
- `sys_rst`: ACTIVE-LOW reset from reset_timer (minimum 200µs hold time)
- `aresetn`: ACTIVE-LOW AXI reset from proc_sys_reset_0
- `S_AXI`: AXI slave interface from SmartConnect

**Outputs**:
- `ui_clk`: **80 MHz** user interface clock (MIG-generated, synchronized to DDR3)
- `ui_clk_sync_rst`: Synchronous reset in ui_clk domain
- `init_calib_complete`: HIGH when calibration done
- `mmcm_locked`: HIGH when internal MMCM locked
- `ddr3_*`: Physical DDR3 interface pins (address, data, control, DQS, etc.)

**DDR3 Pin Assignment**:
- **Bank 34, T0, T1, T2, T3** (ALL DDR3 signals, 1.5V SSTL135 via Internal Vref):
  - Address: ddr3_addr[13:0] (14 bits)
  - Bank select: ddr3_ba[2:0] (3 bits)
  - Control: ddr3_ras_n, ddr3_cas_n, ddr3_we_n, ddr3_cke[0], ddr3_cs_n[0], ddr3_odt[0]
  - Clock: ddr3_ck_p[0], ddr3_ck_n[0] (differential)
  - Reset: ddr3_reset_n
  - Data: ddr3_dq[15:0] (16 bits) with IN_TERM UNTUNED_SPLIT_50
  - Data strobes: ddr3_dqs_p[1:0], ddr3_dqs_n[1:0] (differential)
  - Data mask: ddr3_dm[1:0] (2 bits)
- **Bank 14**: UART at 3.3V (independent VCCO rail, no conflict)

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

#### 6. CPU Core (cpu)
**Purpose**: RISC-V RV32I processor executing instructions from DDR3

**Interfaces**:
- `i_Clock`: MIG `ui_clk` (synchronized to DDR3 timing)
- `i_Reset`: Active-HIGH reset from proc_sys_reset_0
- `i_Init_Calib_Complete`: MIG calibration status signal
- `s_instruction_memory_axil`: AXI-Lite master for instruction fetches
- `s_data_memory_axil`: AXI-Lite master for load/store operations
- `i_Uart_Tx_In`: UART transmit input
- `o_Uart_Rx_Out`: UART receive output

**Key properties**:
- Dual AXI-Lite masters (instruction and data buses)
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

### Signal Flow During Power-On

1. **T=0**: Power on, `ext_reset_in_0` = LOW (ACTIVE-LOW)
2. **T=~1ms**: User releases reset button, `ext_reset_in_0` = HIGH
3. **NOT gate inverts**: Output goes LOW → active-HIGH reset to Clock Wizard
4. **Clock Wizard starts**: PLL begins locking
5. **T=~10ms**: Clock Wizard `locked` = HIGH, PLL outputs **320 MHz**
6. **reset_timer starts**: `i_Enable` = HIGH, counter increments at **320 MHz**
7. **T=10ms to 10ms+200µs**: Counter counts 0→**64000**, `o_Mig_Reset` = LOW
   - MIG `sys_rst` = LOW (held in reset)
   - MIG initialization sequence begins (doesn't proceed far due to reset)
8. **T=10ms+200µs**: Counter reaches **64000**, `o_Mig_Reset` = HIGH, stays HIGH
   - MIG `sys_rst` = HIGH (released from reset)
   - MIG starts DDR3 calibration
9. **T=10ms+200µs+~300ms**: MIG completes calibration
   - `init_calib_complete` = HIGH
   - `ui_clk` stable and running at **80 MHz**
   - `mmcm_locked` = HIGH
10. **proc_sys_reset_0**: Synchronizes, generates `peripheral_aresetn` and `peripheral_reset`
11. **T=system ready**: CPU can execute from DDR3

### XDC Constraints Summary

**Clock pins**:
```
clk_in1_0: R2, LVCMOS33
```

**Reset pins**:
```
ext_reset_in_0: V14, LVCMOS33
```

**UART pins** (Bank 14):
```
i_Uart_Tx_In: V12, LVCMOS33
o_Uart_Rx_Out: R12, LVCMOS33
```

**DDR3 pins** (auto-generated by MIG in Bank 15):
```
Bank 15 (T0, T1, T2) - ALL DDR3 signals at 1.5V (SSTL135 via Internal Vref):
  ddr3_addr[13:0], ddr3_ba[2:0]: SSTL135
  ddr3_ck_p/n[0]: DIFF_SSTL135
  ddr3_ras_n, ddr3_cas_n, ddr3_we_n: SSTL135
  ddr3_cke[0], ddr3_cs_n[0], ddr3_odt[0]: SSTL135
  ddr3_reset_n: SSTL135
  ddr3_dq[15:0]: SSTL135, IN_TERM UNTUNED_SPLIT_50
  ddr3_dqs_p/n[1:0]: DIFF_SSTL135
  ddr3_dm[1:0]: SSTL135
```

**UART pins** (Bank 14 - independent VCCO):
```
Bank 14 (T3) - All UART at 3.3V (LVCMOS33):
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
- DDR3 requires 1.5V SSTL135 with Internal Vref
- **CANNOT mix 3.3V and 1.5V I/O standards on same bank** - VCCO voltage conflict
- This caused MIG calibration to never complete

**Solution 2**:
- **Use Bank 34 for ALL DDR3 signals** (data, address, control)
- Bank 34 has no 3.3V peripherals - can be powered at 1.5V for DDR3
- Bank 15 left unused (or available for 3.3V signals only)

**Final Configuration**:
- ✓ Clock: **320 MHz** sys_clk and ref_clk (3125 ps, within valid range)
- ✓ Bank: **Bank 34** for all DDR3 (no voltage conflicts)
- ✓ Reset: **64,000 cycles @ 320 MHz = 200µs**
- **UI clock**: **80 MHz** (320 ÷ 4 PHY ratio)
- **DDR3 speed**: DDR3-640

**Key lessons**:
1. MIG system clock constraints (3000-3300 ps) limit frequency choices
2. **Bank selection CRITICAL** - must avoid mixing I/O voltage standards on same bank
3. Check schematic for ALL peripherals on selected banks before configuring MIG

---
