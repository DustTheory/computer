#!/usr/bin/env python3
"""Periodically probe the FPGA board via UART debug protocol."""

import serial
import time
import sys
import glob

# Opcodes
OP_HALT       = 0x03
OP_UNHALT     = 0x04
OP_PING       = 0x05
OP_READ_PC    = 0x06
OP_DUMP_STATE = 0x0A

# Data memory AXI states
DATA_MEM_STATES = {0: "IDLE", 1: "RD_SUBMIT", 2: "RD_AWAIT", 3: "RD_OK",
                   4: "WR_SUBMIT", 5: "WR_AWAIT", 6: "WR_OK", 7: "MEM_ERR"}
INSTR_MEM_STATES = {0: "IDLE", 1: "RD_SUBMIT", 2: "RD_AWAIT", 3: "RD_OK"}

PC_LABELS = {
    0x80000010: "fill_loop",
    0x80000014: "fill_loop+4",
    0x80000018: "fill_loop+8",
    0x8000001C: "fill_loop+C (branch)",
    0x80000020: "vdma_init",
    0x80000028: "vdma_ctrl_write",
    0x80000048: "vdma_vsize (trigger)",
    0x8000004C: "ddr3_test",
    0x8000006C: "*** FAIL ***",
    0x80000070: "*** PASS ***",
}

def find_port():
    candidates = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
    if not candidates:
        return None
    # prefer USB1 if multiple
    for p in candidates:
        if "USB1" in p:
            return p
    return candidates[0]

def send_byte(ser, b):
    ser.write(bytes([b]))

def read_bytes(ser, n, timeout=0.5):
    ser.timeout = timeout
    data = ser.read(n)
    return data

def ping(ser):
    send_byte(ser, OP_PING)
    r = read_bytes(ser, 1)
    return len(r) == 1 and r[0] == 0xAA

def read_pc(ser):
    send_byte(ser, OP_READ_PC)
    r = read_bytes(ser, 4)
    if len(r) != 4:
        return None
    return int.from_bytes(r, "little")

def dump_state(ser):
    send_byte(ser, OP_DUMP_STATE)
    r = read_bytes(ser, 2)
    if len(r) != 2:
        return None
    b0, b1 = r[0], r[1]
    return {
        "data_mem":         DATA_MEM_STATES.get((b0 >> 5) & 0x7, "?"),
        "pipeline_flushed": bool(b0 & 0x10),
        "stall_s1":         bool(b0 & 0x08),
        "enable_fetch":     bool(b0 & 0x04),
        "s2_valid":         bool(b0 & 0x02),
        "s3_valid":         bool(b0 & 0x01),
        "instr_mem":        INSTR_MEM_STATES.get((b1 >> 6) & 0x3, "?"),
        "init_calib":       bool(b1 & 0x20),
    }

def probe_once(ser):
    send_byte(ser, OP_HALT)
    time.sleep(0.01)

    pc = read_pc(ser)
    state = dump_state(ser)

    send_byte(ser, OP_UNHALT)

    return pc, state

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    if not port:
        print("No serial port found. Usage: probe.py [/dev/ttyUSBx]")
        sys.exit(1)

    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    print(f"Opening {port} @ 115200 baud")
    ser = serial.Serial(port, 115200, timeout=0.5)
    time.sleep(0.1)

    # flush
    ser.reset_input_buffer()

    if not ping(ser):
        print("PING failed — check connection")
        ser.close()
        sys.exit(1)
    print("PING OK\n")

    prev_pc = None
    while True:
        try:
            pc, state = probe_once(ser)
            ts = time.strftime("%H:%M:%S")

            if pc is None or state is None:
                print(f"[{ts}] read error")
            else:
                label = PC_LABELS.get(pc, "")
                pc_str = f"0x{pc:08X}"
                if label:
                    pc_str += f"  ({label})"

                changed = pc != prev_pc
                prev_pc = pc

                calib = "CAL" if state["init_calib"] else "no-cal"
                dm = state["data_mem"]
                im = state["instr_mem"]
                flags = ""
                if state["pipeline_flushed"]: flags += " FLUSHED"
                if state["stall_s1"]:         flags += " STALL"
                if not state["enable_fetch"]: flags += " no-fetch"

                marker = ">>>" if changed else "   "
                print(f"[{ts}] {marker} PC={pc_str}  dm={dm:8s} im={im:8s} {calib}{flags}")

            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nDone.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(interval)

    ser.close()

if __name__ == "__main__":
    main()
