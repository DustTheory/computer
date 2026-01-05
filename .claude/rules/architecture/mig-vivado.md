---
paths:
  - hdl/reset_timer.v
  - config/arty-s7-50.xdc
---

# MIG DDR3 Configuration (Arty S7-50)

**Last updated**: 2026-01-05
**Status**: ✅ MIG CALIBRATION SUCCESSFUL - DDR3 functional @ 81.25 MHz

## Critical Success Factors

**MUST HAVE** for DDR3 calibration:
1. **200 MHz reference clock** to MIG `clk_ref_i` (MANDATORY for IDELAYCTRL - won't calibrate without it)
2. **Bank 34 only** for all DDR3 signals (SSTL135 @ 1.35V)
3. **200µs reset hold time** for MIG `sys_rst` (20,000 cycles @ 100 MHz)
4. CPU reset from `ui_clk_sync_rst`, NOT `peripheral_reset` (stays HIGH)

**Vivado project**: NOT in repository (binary files, too large). Recreate from notes below if needed.

## Working MIG Configuration

**Memory part**: MT41K128M16XX-15E
- 16-bit DDR3L, 128 Mb, -15E speed grade, **1.35V operation**
- I/O standard: **SSTL135** (NOT SSTL15)
- Bank: **Bank 34 only** (all byte groups: DQ[0-15], Address/Ctrl)
- Internal Vref: ENABLED (0.675V for Bank 34)

**MIG Parameters**:
- AXI interface: 128-bit data width (SmartConnect converts from CPU's 32-bit)
- Address width: 28-bit
- Input clock period: 10000 ps (100 MHz) → `sys_clk_i`
- Memory clock: 3077 ps (324.99 MHz, MIG-generated internally)
- Reference clock: **200 MHz (5000 ps)** → `clk_ref_i` ⚠️ CRITICAL
- PHY ratio: 4:1
- **UI clock: 81.25 MHz** (324.99 MHz ÷ 4) - CPU runs at this speed

## Clock Architecture

**Input**: 12 MHz from board oscillator (pin F14, LVCMOS33)

**Clock Wizard** (MMCM):
- VCO: 12 MHz × 50 = 600 MHz
- Output 1: **100 MHz** (÷6) → MIG `sys_clk_i` + reset_timer
- Output 2: **200 MHz** (÷3) → MIG `clk_ref_i` ⚠️ CRITICAL

**MIG-generated**:
- Memory interface: 324.99 MHz (internal)
- UI clock: **81.25 MHz** (CPU domain)

## Reset Architecture

**Custom reset timer** ([reset_timer.v](hdl/reset_timer.v)):
- Counts **20,000 cycles @ 100 MHz = 200µs**
- Holds MIG `sys_rst` LOW during startup (ACTIVE-LOW reset)
- Releases when count completes
- Parameters: `COUNTER_WIDTH=15`, `HOLD_CYCLES=20000`

**CPU reset**:
- Connected to MIG's `ui_clk_sync_rst` (ACTIVE-HIGH, synchronized to ui_clk)
- ❌ **NOT using** `proc_sys_reset_0/peripheral_reset` (stays perpetually HIGH - known issue)

## Bank Selection - CRITICAL

**Why Bank 34 only**:
- Bank 34: Powered at **1.35V** for DDR3L (SSTL135)
- Bank 15: Has RGB LEDs requiring **3.3V** (LVCMOS33) - voltage conflict with DDR3
- Bank 14: UART signals (**3.3V** LVCMOS33)
- **Separate banks = independent VCCO rails** = no voltage conflict

**All DDR3 signals must be on Bank 34**:
- DQ[0-7] (Byte Group T0)
- DQ[8-15] (Byte Group T1)
- Address/Control-0 (Byte Group T2)
- Address/Control-1 (Byte Group T3)

## Key Lessons

1. **200 MHz ref_clk is MANDATORY**: DDR3 WILL NOT calibrate without it (IDELAYCTRL requirement)
2. **Bank voltage isolation**: Check board schematic for VCCO rail voltages before assigning pins
3. **SSTL135 for DDR3L**: Use SSTL135 (1.35V), NOT SSTL15 (1.5V) - wrong I/O standard prevents calibration
4. **Reset timing matters**: MIG requires minimum 200µs reset hold time
5. **ui_clk_sync_rst for CPU**: Use MIG's `ui_clk_sync_rst`, not Processor System Reset IP (broken output)

## Vivado Block Diagram Components

**If recreating from scratch**:

1. **Clock Wizard**:
   - Input: 12 MHz
   - Outputs: 100 MHz (sys_clk), 200 MHz (ref_clk)

2. **Reset Timer** (custom Verilog):
   - Input: 100 MHz clock, Clock Wizard `locked`
   - Output: ACTIVE-LOW reset to MIG `sys_rst`
   - Hold: 20,000 cycles

3. **MIG 7-Series**:
   - Part: MT41K128M16XX-15E
   - Clocks: 100 MHz sys_clk_i, 200 MHz clk_ref_i
   - AXI: 128-bit interface
   - Bank: 34 (SSTL135)
   - Internal Vref: ENABLED

4. **AXI SmartConnect**:
   - Masters: CPU instruction + data (32-bit each)
   - Slave: MIG (128-bit)
   - Handles width conversion

5. **Processor System Reset**:
   - Generates AXI reset signals for MIG/SmartConnect
   - **Do NOT use for CPU reset** (use ui_clk_sync_rst instead)

## Troubleshooting

**Calibration fails**:
- Check 200 MHz ref_clk connected to MIG `clk_ref_i`
- Verify Bank 34 for all DDR3 pins
- Verify SSTL135 I/O standard (not SSTL15)
- Check reset hold time (minimum 200µs)

**Wrong data/corruption**:
- Verify AXI connections (SmartConnect to MIG)
- Check ui_clk domain crossing
- Verify CPU reset from ui_clk_sync_rst

**Build errors**:
- Vivado project not in repo - must recreate block diagram
- Constraint file: [arty-s7-50.xdc](config/arty-s7-50.xdc) has pin assignments

## Reference

**Board**: Arty S7-50 (xc7s50-csga324, speed grade -1)
**Memory**: 256 MB DDR3L @ 1.35V (MT41K128M16XX-15E)
**Oscillator**: 12 MHz (pin F14)

See Arty S7 reference manual for schematic and VCCO rail assignments.
