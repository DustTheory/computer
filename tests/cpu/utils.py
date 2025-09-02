from cpu.constants import (
    OP_B_TYPE,
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