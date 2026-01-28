#!/usr/bin/env python3
"""Simple RISC-V assembler for the fill_screen program."""

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

# Register mapping
regs = {
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
    't0': 5, 't1': 6, 't2': 7, 't3': 8, 't4': 9, 't5': 10, 't6': 11,
    's0': 8, 's1': 9, 's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
}

# Opcodes
OP_LUI    = 0b0110111
OP_AUIPC  = 0b0010111
OP_JAL    = 0b1101111
OP_JALR   = 0b1100111
OP_BRANCH = 0b1100011
OP_LOAD   = 0b0000011
OP_STORE  = 0b0100011
OP_ALU_I  = 0b0010011
OP_ALU_R  = 0b0110011

# Sign extend a value to 32 bits
def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

# Two's complement for negative immediates
def to_twos_complement(value, bits):
    if value < 0:
        return (1 << bits) + value
    return value

# Assemble the program
program = []

# lui t0, 0x87F1E
program.append(encode_u_type(OP_LUI, regs['t0'], 0x87F1E))

# lui t2, 0xFFFFF
program.append(encode_u_type(OP_LUI, regs['t2'], 0xFFFFF & 0xFFFFF))

# addi t2, t2, -1
program.append(encode_i_type(OP_ALU_I, regs['t2'], 0, regs['t2'], to_twos_complement(-1, 12)))

# lui t1, 0x26
program.append(encode_u_type(OP_LUI, regs['t1'], 0x26))

# addi t1, t1, -0x800
program.append(encode_i_type(OP_ALU_I, regs['t1'], 0, regs['t1'], to_twos_complement(-0x800, 12)))

# fill_loop (PC = 0x14):
# sw t2, 0(t0)
program.append(encode_s_type(OP_STORE, 2, regs['t0'], regs['t2'], 0))  # funct3=2 for SW

# addi t0, t0, 4
program.append(encode_i_type(OP_ALU_I, regs['t0'], 0, regs['t0'], 4))

# addi t1, t1, -1
program.append(encode_i_type(OP_ALU_I, regs['t1'], 0, regs['t1'], to_twos_complement(-1, 12)))

# bne t1, zero, fill_loop (offset = -16 bytes = -4 instructions)
program.append(encode_b_type(OP_BRANCH, 1, regs['t1'], regs['zero'], to_twos_complement(-16, 13)))  # funct3=1 for BNE

# configure_vdma:
# lui t3, 0x88000
program.append(encode_u_type(OP_LUI, regs['t3'], 0x88000 & 0xFFFFF))

# lui t4, 0x87F1E
program.append(encode_u_type(OP_LUI, regs['t4'], 0x87F1E))

# sw t4, 0x18(t3)
program.append(encode_s_type(OP_STORE, 2, regs['t3'], regs['t4'], 0x18))

# lui t4, 0
program.append(encode_u_type(OP_LUI, regs['t4'], 0))

# addi t4, zero, 0x500
program.append(encode_i_type(OP_ALU_I, regs['t4'], 0, regs['zero'], 0x500))

# sw t4, 0x24(t3)
program.append(encode_s_type(OP_STORE, 2, regs['t3'], regs['t4'], 0x24))

# sw t4, 0x28(t3)
program.append(encode_s_type(OP_STORE, 2, regs['t3'], regs['t4'], 0x28))

# addi t4, zero, 0x1E0
program.append(encode_i_type(OP_ALU_I, regs['t4'], 0, regs['zero'], 0x1E0))

# sw t4, 0x20(t3)
program.append(encode_s_type(OP_STORE, 2, regs['t3'], regs['t4'], 0x20))

# addi t4, zero, 0x13
program.append(encode_i_type(OP_ALU_I, regs['t4'], 0, regs['zero'], 0x13))

# sw t4, 0x00(t3)
program.append(encode_s_type(OP_STORE, 2, regs['t3'], regs['t4'], 0x00))

# done:
# jal zero, done (offset = 0, infinite loop)
program.append(encode_j_type(OP_JAL, regs['zero'], 0))

# Print the program
print("Assembled program:")
for i, instr in enumerate(program):
    print(f"0x{i*4:04X}: 0x{instr:08X}")

# Write to hex file (Verilog $readmemh format)
with open('fill_screen.rom', 'w') as f:
    for instr in program:
        f.write(f"{instr:08x}\n")

print(f"\nWrote {len(program)} instructions to fill_screen.rom")
print(f"Program size: {len(program) * 4} bytes")
