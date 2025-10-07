from cpu.constants import (
    OP_B_TYPE,
    OP_S_TYPE,
    OP_R_TYPE,
)

def gen_i_type_instruction(opcode, rd, funct3, rs1, imm):
    instruction = opcode
    instruction |= rd << 7
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= (imm & 0b111111111111) << 20
    return instruction

def gen_b_type_instruction(funct3, rs1, rs2, offset):
    opcode = OP_B_TYPE
    instruction = opcode
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= rs2 << 20

    imm_12 = (offset >> 12) & 0x1
    imm_10_5 = (offset >> 5) & 0x3F
    imm_4_1 = (offset >> 1) & 0xF
    imm_11 = (offset >> 11) & 0x1

    instruction |= imm_11 << 7
    instruction |= imm_4_1 << 8
    instruction |= imm_10_5 << 25
    instruction |= imm_12 << 31

    return instruction

def gen_s_type_instruction(funct3, rs1, rs2, imm):
    opcode = OP_S_TYPE
    instruction = opcode
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= rs2 << 20

    imm_4_0 = imm & 0b11111
    imm_11_5 = (imm >> 5) & 0b1111111

    instruction |= imm_4_0 << 7
    instruction |= imm_11_5 << 25

    return instruction

def gen_r_type_instruction(rd, funct3, rs1, rs2, funct7):
    instruction = OP_R_TYPE
    instruction |= rd << 7
    instruction |= funct3 << 12
    instruction |= rs1 << 15
    instruction |= rs2 << 20
    instruction |= funct7 << 25
    return instruction

# New helper utilities for byte-addressable test memory access

def write_word_to_mem(mem_array, addr, value):
    """Write a 32-bit value into byte-addressable cocotb memory (little-endian)."""
    mem_array[addr + 0].value = (value >> 0) & 0xFF
    mem_array[addr + 1].value = (value >> 8) & 0xFF
    mem_array[addr + 2].value = (value >> 16) & 0xFF
    mem_array[addr + 3].value = (value >> 24) & 0xFF

def write_half_to_mem(mem_array, addr, value):
    mem_array[addr + 0].value = (value >> 0) & 0xFF
    mem_array[addr + 1].value = (value >> 8) & 0xFF

def write_byte_to_mem(mem_array, addr, value):
    mem_array[addr].value = value & 0xFF

def write_instructions(mem_array, base_addr, instructions):
    """Write a list of 32-bit instructions at word stride (4 bytes)."""
    for i, ins in enumerate(instructions):
        write_word_to_mem(mem_array, base_addr + 4*i, ins)