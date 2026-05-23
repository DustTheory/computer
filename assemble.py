#!/usr/bin/env python3
"""RISC-V assembler: fill framebuffer, init VDMA, then test DDR3 load/store."""

def encode_r_type(opcode, rd, funct3, rs1, rs2, funct7):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_i_type(opcode, rd, funct3, rs1, imm):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_s_type(opcode, funct3, rs1, rs2, imm):
    imm_11_5 = (imm >> 5) & 0x7F
    imm_4_0 = imm & 0x1F
    return (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode

def encode_b_type(opcode, funct3, rs1, rs2, imm):
    imm_12 = (imm >> 12) & 0x1
    imm_11 = (imm >> 11) & 0x1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    return (imm_12 << 31) | (imm_10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_1 << 8) | (imm_11 << 7) | opcode

def encode_u_type(opcode, rd, imm):
    return (imm << 12) | (rd << 7) | opcode

def encode_j_type(opcode, rd, imm):
    imm_20 = (imm >> 20) & 0x1
    imm_19_12 = (imm >> 12) & 0xFF
    imm_11 = (imm >> 11) & 0x1
    imm_10_1 = (imm >> 1) & 0x3FF
    return (imm_20 << 31) | (imm_10_1 << 21) | (imm_11 << 20) | (imm_19_12 << 12) | (rd << 7) | opcode

def tc(value, bits):
    """Two's complement encoding for negative immediates."""
    if value < 0:
        return (1 << bits) + value
    return value

# Register numbers
t0, t1, t2, t3, t4, t5 = 5, 6, 7, 8, 9, 10
zero = 0

OP_LUI    = 0b0110111
OP_JAL    = 0b1101111
OP_BRANCH = 0b1100011
OP_LOAD   = 0b0000011
OP_STORE  = 0b0100011
OP_ALU_I  = 0b0010011
OP_ALU_R  = 0b0110011

program = []

# ── Fill framebuffer ──────────────────────────────────────────────────────────
# t0 = 0x87F1E000 (framebuffer base in DDR3)
# t2 = 0xF000F000 (two red pixels: R=0xF, G=0, B=0 in R[15:12]/G[10:7]/B[4:1])
# t1 = 153600 (640×480×2 bytes / 4 bytes per SW = word count)

# 0x00
program.append(encode_u_type(OP_LUI, t0, 0x87F1E))         # lui t0, 0x87F1E
# 0x04
program.append(encode_u_type(OP_LUI, t2, 0xF000F))         # lui t2, 0xF000F  (= 0xF000F000)
# 0x08
program.append(encode_u_type(OP_LUI, t1, 0x26))            # lui t1, 0x26000
# 0x0C
program.append(encode_i_type(OP_ALU_I, t1, 0, t1, tc(-0x800, 12)))  # addi t1, t1, -2048  → 153600

# fill_loop: offset 0x10
# 0x10
program.append(encode_s_type(OP_STORE, 2, t0, t2, 0))      # sw t2, 0(t0)
# 0x14
program.append(encode_i_type(OP_ALU_I, t0, 0, t0, 4))      # addi t0, t0, 4
# 0x18
program.append(encode_i_type(OP_ALU_I, t1, 0, t1, tc(-1, 12)))  # addi t1, t1, -1
# 0x1C  branch back to fill_loop (offset 0x10), delta = -12
program.append(encode_b_type(OP_BRANCH, 1, t1, zero, tc(-12, 13)))  # bne t1, zero, -12

# ── Configure VDMA (correct offsets from PG020 / component.xml) ───────────────
# Register map (base = 0x88000000):
#   0x00  MM2S_VDMACR  - control (RS=1 bit0, Circular=1 bit1)
#   0x54  MM2S_HSIZE   - horizontal size in bytes
#   0x58  MM2S_FRMDLY_STRIDE - [15:0]=stride bytes
#   0x5C  MM2S_SA1     - frame buffer start address (frame 1)
#   0x60  MM2S_SA2     - frame buffer start address (frame 2, same for single-buf)
#   0x50  MM2S_VSIZE   - vertical lines  ← WRITING THIS TRIGGERS DMA, must be last

# 0x20
program.append(encode_u_type(OP_LUI, t3, 0x88000))         # lui t3, 0x88000  (= 0x88000000)
# 0x24
program.append(encode_i_type(OP_ALU_I, t4, 0, zero, 3))    # addi t4, zero, 3  (RS|Circular)
# 0x28
program.append(encode_s_type(OP_STORE, 2, t3, t4, 0x00))   # sw t4, 0(t3)   VDMA[0x00]=0x3
# 0x2C
program.append(encode_u_type(OP_LUI, t4, 0x87F1E))         # lui t4, 0x87F1E (framebuf addr)
# 0x30
program.append(encode_s_type(OP_STORE, 2, t3, t4, 0x5C))   # sw t4, 0x5C(t3)  SA1
# 0x34
program.append(encode_s_type(OP_STORE, 2, t3, t4, 0x60))   # sw t4, 0x60(t3)  SA2 (same addr)
# 0x38
program.append(encode_i_type(OP_ALU_I, t4, 0, zero, 1280)) # addi t4, zero, 1280
# 0x3C
program.append(encode_s_type(OP_STORE, 2, t3, t4, 0x58))   # sw t4, 0x58(t3)  STRIDE
# 0x40
program.append(encode_s_type(OP_STORE, 2, t3, t4, 0x54))   # sw t4, 0x54(t3)  HSIZE
# 0x44
program.append(encode_i_type(OP_ALU_I, t4, 0, zero, 480))  # addi t4, zero, 480
# 0x48  VSIZE last — triggers DMA
program.append(encode_s_type(OP_STORE, 2, t3, t4, 0x50))   # sw t4, 0x50(t3)  VSIZE → start!

# ── DDR3 load/store test ──────────────────────────────────────────────────────
# Store 0xABCD0000 to first DDR3 RAM address (0x80001000), then load it back.
# PASS: PC stuck at 0x80000070
# FAIL: PC stuck at 0x8000006C

# 0x4C
program.append(encode_u_type(OP_LUI, t0, 0x80001))         # lui t0, 0x80001  (= 0x80001000)
# 0x50
program.append(encode_u_type(OP_LUI, t1, 0xABCD0))         # lui t1, 0xABCD0  (= 0xABCD0000)
# 0x54
program.append(encode_s_type(OP_STORE, 2, t0, t1, 0))      # sw t1, 0(t0)
# 0x58  filler ops (pipeline flushers)
program.append(encode_i_type(OP_ALU_I, t2, 0, zero, 42))   # addi t2, zero, 42
# 0x5C
program.append(encode_i_type(OP_ALU_I, t3, 0, t2, 100))    # addi t3, t2, 100
# 0x60
program.append(encode_r_type(OP_ALU_R, t4, 0, t2, t3, 0))  # add t4, t2, t3
# 0x64
program.append(encode_i_type(OP_LOAD, t5, 2, t0, 0))       # lw t5, 0(t0)
# 0x68  branch to PASS if t5 == t1, else fall through to FAIL
program.append(encode_b_type(OP_BRANCH, 0, t5, t1, 8))     # beq t5, t1, +8

# FAIL — PC = 0x8000006C
# 0x6C
program.append(encode_j_type(OP_JAL, zero, 0))             # jal zero, 0  (infinite loop)

# PASS — PC = 0x80000070
# 0x70
program.append(encode_j_type(OP_JAL, zero, 0))             # jal zero, 0  (infinite loop)

# ── Output ────────────────────────────────────────────────────────────────────
print("Assembled program:")
for i, instr in enumerate(program):
    print(f"  0x{i*4:04X} (PC=0x{0x80000000+i*4:08X}):  {instr:08x}")

print(f"\nTotal: {len(program)} instructions ({len(program)*4} bytes)")
print(f"\nDDR3 test results (read PC via debugger):")
print(f"  PASS = PC stuck at 0x80000070")
print(f"  FAIL = PC stuck at 0x8000006C")

with open('rom.mem', 'w') as f:
    for instr in program:
        f.write(f"{instr:08x}\n")

print(f"\nWrote rom.mem")
